from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import CONF_COUNTRY, CONF_PROVINCE, CONF_LANGUAGE, CONF_UPDATE_INTERVAL, DEFAULT_COUNTRY, DEFAULT_LANGUAGE, DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_COUNTRY, default=DEFAULT_COUNTRY): str,
                        vol.Required(CONF_PROVINCE): str,
                        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): str,
                        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                    }
                ),
            )

        return self.async_create_entry(title=user_input[CONF_PROVINCE], data=user_input)