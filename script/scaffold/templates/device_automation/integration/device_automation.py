"""Provides device automations for NEW_NAME."""
from typing import Callable, Optional, List
import voluptuous as vol

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_DOMAIN,
    CONF_TYPE,
    CONF_PLATFORM,
    CONF_DEVICE_ID,
    CONF_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.core import HomeAssistant, Context, CALLBACK_TYPE
from homeassistant.helpers import condition, entity_registry
from homeassistant.helpers.typing import ConfigType, TemplateVarsType
from homeassistant.helpers.config_validation import (
    DEVICE_ACTION_SCHEMA,
    DEVICE_CONDITION_SCHEMA,
)
from homeassistant.components.automation import state
from homeassistant.components.device_automation import (  # noqa  # pylint: disable=unused-import
    TRIGGER_SCHEMA,
)
from . import DOMAIN

# Types of supported triggers, conditions and actions
TRIGGER_TYPES = {"turned_on", "turned_off"}
CONDITION_TYPES = {"is_on"}
ACTION_TYPES = {"turn_on", "turn_off"}

TRIGGER_SCHEMA = TRIGGER_SCHEMA.extend({vol.Required(CONF_TYPE): TRIGGER_TYPES})

CONDITION_SCHEMA = DEVICE_CONDITION_SCHEMA.extend(
    {vol.Required(CONF_TYPE): CONDITION_TYPES}
)

ACTION_SCHEMA = DEVICE_ACTION_SCHEMA.extend({vol.Required(CONF_TYPE): ACTION_TYPES})


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> List[dict]:
    """List device triggers for NEW_NAME devices."""
    registry = await entity_registry.async_get_registry(hass)
    triggers = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        # Add triggers for each entity that belongs to this integration
        # TODO add your own triggers. It's ok to not have any triggers.
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_on",
            }
        )
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_off",
            }
        )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: dict,
    action: Callable[..., None],
    automation_info: dict,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    config = TRIGGER_SCHEMA(config)

    if config[CONF_TYPE] == "turned_on":
        from_state = STATE_OFF
        to_state = STATE_ON
    else:
        from_state = STATE_ON
        to_state = STATE_OFF

    return state.async_trigger(
        hass,
        {
            CONF_ENTITY_ID: config[CONF_ENTITY_ID],
            state.CONF_FROM: from_state,
            state.CONF_TO: to_state,
        },
        action,
        automation_info,
        platform_type="device",
    )


async def async_get_conditions(hass: HomeAssistant, device_id: str):
    """List device conditions for NEW_NAME devices."""
    registry = await entity_registry.async_get_registry(hass)
    conditions = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        # Add conditions for each entity that belongs to this integration
        # TODO add your own conditions. It's ok to not have any conditions.
        conditions.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "is_on",
            }
        )

    return conditions


def async_condition_from_config(
    config: ConfigType, config_validation: bool = True
) -> condition.ConditionChecker:
    """Create a function to test a device condition."""
    if config_validation:
        config = CONDITION_SCHEMA(config)

    def test_is_on(hass: HomeAssistant, variables: TemplateVarsType) -> bool:
        """Test if an entity is on."""
        return condition.state(hass, config[ATTR_ENTITY_ID], STATE_ON)

    return test_is_on


async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[dict]:
    """List device actions for NEW_NAME devices."""
    registry = await entity_registry.async_get_registry(hass)
    actions = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        # Add actions for each entity that belongs to this integration
        # TODO add your own actions. It's ok to not have any actions.
        actions.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turn_on",
            }
        )
        actions.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turn_off",
            }
        )

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant, config: dict, variables: dict, context: Optional[Context]
):
    """Execute a device action."""
    config = ACTION_SCHEMA(config)

    service_data = {ATTR_ENTITY_ID: config[CONF_ENTITY_ID]}

    if config[CONF_TYPE] == "turn_on":
        service = SERVICE_TURN_ON
    elif config[CONF_TYPE] == "turn_off":
        service = SERVICE_TURN_OFF

    await hass.services.async_call(
        DOMAIN, service, service_data, blocking=True, context=context
    )
