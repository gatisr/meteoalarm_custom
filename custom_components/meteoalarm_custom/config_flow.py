"""Config flow for the MeteoAlarm integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    LanguageSelector,
    LanguageSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from homeassistant.util import slugify

from .api import (
    MeteoAlarmConnectionError,
    MeteoAlarmRegion,
    MeteoAlarmUnsupportedCountryError,
    async_get_regions,
)
from .const import (
    CONF_COUNTRY,
    CONF_GEOCODE,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_UPDATE_INTERVAL,
    COUNTRIES,
    DEFAULT_COUNTRY,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)


class MeteoAlarmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeteoAlarm."""

    VERSION = 3

    def __init__(self) -> None:
        """Initialize the flow."""
        self._country: str | None = None
        self._regions: list[MeteoAlarmRegion] = []
        self._feed_available = False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the country."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Custom slugs are allowed so new/renamed feeds keep working;
            # validate them by fetching the feed once.
            country = user_input[CONF_COUNTRY].strip().lower()
            self._regions = []
            self._feed_available = False
            try:
                self._regions = await async_get_regions(
                    async_get_clientsession(self.hass), country
                )
                self._feed_available = True
            except MeteoAlarmUnsupportedCountryError:
                errors[CONF_COUNTRY] = "invalid_country"
            except MeteoAlarmConnectionError:
                if country not in COUNTRIES:
                    # Cannot verify a custom slug without a connection.
                    errors[CONF_COUNTRY] = "cannot_connect"

            if not errors:
                self._country = country
                return await self.async_step_region()

        country_options = [
            SelectOptionDict(value=slug, label=name)
            for slug, name in sorted(COUNTRIES.items(), key=lambda kv: kv[1])
        ]
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_COUNTRY,
                    default=(user_input or {}).get(CONF_COUNTRY, DEFAULT_COUNTRY),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=country_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_region(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the region and options."""
        assert self._country is not None
        errors: dict[str, str] = {}

        if user_input is not None:
            province = user_input[CONF_PROVINCE].strip()
            if not province:
                errors[CONF_PROVINCE] = "invalid_province"
            else:
                await self.async_set_unique_id(
                    f"{self._country}_{slugify(province)}"
                )
                self._abort_if_unique_id_configured()

                geocode = next(
                    (
                        region.geocode
                        for region in self._regions
                        if region.name == province
                    ),
                    None,
                )
                data = {
                    CONF_COUNTRY: self._country,
                    CONF_PROVINCE: province,
                    CONF_GEOCODE: geocode,
                }
                options = {
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_UPDATE_INTERVAL: int(user_input[CONF_UPDATE_INTERVAL]),
                }
                return self.async_create_entry(
                    title=province, data=data, options=options
                )

        region_options = [
            SelectOptionDict(value=region.name, label=region.name)
            for region in self._regions
        ]
        schema = vol.Schema(
            {
                vol.Required(CONF_PROVINCE): SelectSelector(
                    SelectSelectorConfig(
                        options=region_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                        sort=True,
                    )
                ),
                vol.Required(
                    CONF_LANGUAGE, default=self.hass.config.language.split("-")[0]
                ): LanguageSelector(LanguageSelectorConfig()),
                vol.Required(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=1440,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="region",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "country": COUNTRIES.get(self._country, self._country),
                "region_count": str(len(self._regions)),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> MeteoAlarmOptionsFlow:
        """Create the options flow."""
        return MeteoAlarmOptionsFlow()


class MeteoAlarmOptionsFlow(OptionsFlowWithReload):
    """Change language and update interval after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_UPDATE_INTERVAL: int(user_input[CONF_UPDATE_INTERVAL]),
                }
            )

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LANGUAGE, default=options.get(CONF_LANGUAGE, "en")
                ): LanguageSelector(LanguageSelectorConfig()),
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=1440,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
