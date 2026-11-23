"""Config flow for the MeteoAlarm integration."""

from __future__ import annotations

import re
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
    MeteoAlarmParseError,
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
from .shared import get_feed_cache, get_known_regions


# Custom slugs end up in the feed URL path.
_SLUG_RE = re.compile(r"[a-z0-9-]+")


class MeteoAlarmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeteoAlarm."""

    VERSION = 3

    def __init__(self) -> None:
        """Initialize the flow."""
        self._country: str | None = None
        self._regions: list[MeteoAlarmRegion] = []
        self._feed_available = False

    async def _async_load_regions(self, country: str) -> str | None:
        """Fill ``self._regions`` (feed + remembered); return an error key or None."""
        if not _SLUG_RE.fullmatch(country):
            return "invalid_country"
        known = get_known_regions(self.hass)
        self._regions = []
        self._feed_available = False
        error: str | None = None
        try:
            self._regions = await async_get_regions(
                async_get_clientsession(self.hass), country, get_feed_cache(self.hass)
            )
            self._feed_available = True
            await known.async_add(country, self._regions)
        except MeteoAlarmUnsupportedCountryError:
            error = "invalid_country"
        except (MeteoAlarmConnectionError, MeteoAlarmParseError):
            if country not in COUNTRIES:
                # Cannot verify a custom slug without a connection.
                error = "cannot_connect"

        if error is None:
            seen = {region.name.casefold() for region in self._regions}
            self._regions = sorted(
                [
                    *self._regions,
                    *(
                        region
                        for region in await known.async_get(country)
                        if region.name.casefold() not in seen
                    ),
                ],
                key=lambda region: region.name,
            )
        return error

    @staticmethod
    def _country_schema(default: str) -> vol.Schema:
        country_options = [
            SelectOptionDict(value=slug, label=name)
            for slug, name in sorted(COUNTRIES.items(), key=lambda kv: kv[1])
        ]
        return vol.Schema(
            {
                vol.Required(CONF_COUNTRY, default=default): SelectSelector(
                    SelectSelectorConfig(
                        options=country_options,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                )
            }
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the country."""
        errors: dict[str, str] = {}

        if user_input is not None:
            country = user_input[CONF_COUNTRY].strip().lower()
            if error := await self._async_load_regions(country):
                errors[CONF_COUNTRY] = error
            else:
                self._country = country
                return await self.async_step_region()

        return self.async_show_form(
            step_id="user",
            data_schema=self._country_schema(
                (user_input or {}).get(CONF_COUNTRY, DEFAULT_COUNTRY)
            ),
            errors=errors,
        )

    # -- reconfigure -----------------------------------------------------------

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the country of an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            country = user_input[CONF_COUNTRY].strip().lower()
            if error := await self._async_load_regions(country):
                errors[CONF_COUNTRY] = error
            else:
                self._country = country
                return await self.async_step_reconfigure_region()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._country_schema(
                (user_input or {}).get(CONF_COUNTRY, entry.data[CONF_COUNTRY])
            ),
            errors=errors,
        )

    async def async_step_reconfigure_region(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the region of an existing entry."""
        assert self._country is not None
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            province = user_input[CONF_PROVINCE].strip()
            if not province:
                errors[CONF_PROVINCE] = "invalid_province"
            else:
                unique_id = f"{self._country}_{slugify(province)}"
                other = self.hass.config_entries.async_entry_for_domain_unique_id(
                    DOMAIN, unique_id
                )
                if other and other.entry_id != entry.entry_id:
                    return self.async_abort(reason="already_configured")
                return self.async_update_reload_and_abort(
                    entry,
                    unique_id=unique_id,
                    title=province,
                    data_updates={
                        CONF_COUNTRY: self._country,
                        CONF_PROVINCE: province,
                        CONF_GEOCODE: self._geocode_for(province),
                    },
                )

        same_country = self._country == entry.data[CONF_COUNTRY]
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PROVINCE,
                    default=entry.data[CONF_PROVINCE] if same_country else vol.UNDEFINED,
                ): self._region_selector()
            }
        )
        return self.async_show_form(
            step_id="reconfigure_region",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "country": COUNTRIES.get(self._country, self._country),
                "region_count": str(len(self._regions)),
            },
        )

    def _geocode_for(self, province: str) -> str | None:
        return next(
            (
                region.geocode
                for region in self._regions
                if region.name.casefold() == province.casefold()
            ),
            None,
        )

    def _region_selector(self) -> SelectSelector:
        return SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value=region.name, label=region.name)
                    for region in self._regions
                ],
                mode=SelectSelectorMode.DROPDOWN,
                custom_value=True,
                sort=True,
            )
        )

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

                geocode = self._geocode_for(province)
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

        schema = vol.Schema(
            {
                vol.Required(CONF_PROVINCE): self._region_selector(),
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
