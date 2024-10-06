from homeassistant import config_entries, data_entry_flow
from custom_components.meteoalarm_custom.config_flow import ConfigFlow

async def test_config_flow(hass):
    flow = ConfigFlow()
    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM

    result = await flow.async_step_user(
        {
            "country": "latvia",
            "province": "LV001",
            "language": "en",
        }
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "LV001"
    assert result["data"] == {
        "country": "latvia",
        "province": "LV001", 
        "language": "en",
    }