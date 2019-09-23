"""Offer device oriented automation."""

from homeassistant.const import CONF_DOMAIN
from homeassistant.loader import async_get_integration
from homeassistant.components.device_automation import (  # noqa  # pylint: disable=unused-import
    TRIGGER_SCHEMA,
)

# mypy: allow-untyped-defs, no-check-untyped-defs


async def async_trigger(hass, config, action, automation_info):
    """Listen for device triggers."""
    integration = await async_get_integration(hass, config[CONF_DOMAIN])
    platform = integration.get_platform("device_automation")
    return await platform.async_attach_trigger(hass, config, action, automation_info)
