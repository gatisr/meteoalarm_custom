from pytest_homeassistant_custom_component.common import load_fixture
import pytest
import os

pytest_plugins = "pytest_homeassistant_custom_component"

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield