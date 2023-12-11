"""The trafikverket_camera component."""
from __future__ import annotations

from typing import Any

from pytrafikverket.trafikverket import (
    AndFilter,
    FieldFilter,
    FilterOperation,
    Trafikverket,
)
from pytrafikverket.trafikverket_camera import CAMERA_INFO_REQUIRED_FIELDS, CameraInfo
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .coordinator import TVDataUpdateCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _: ConfigType) -> bool:
    """Set up all the websockets for Trafikverket Camera."""
    websocket_api.async_register_command(hass, add)
    websocket_api.async_register_command(hass, get_cameras)
    websocket_api.async_register_command(hass, remove)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trafikverket Camera from a config entry."""

    for camera in entry.data.get("cameras", []):
        coordinator = TVDataUpdateCoordinator(hass, entry, camera)
        await coordinator.async_config_entry_first_refresh()
        hass.data.setdefault(DOMAIN, {})[f"{entry.entry_id}/{camera}"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Trafikverket Camera config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


@websocket_api.websocket_command(
    {
        vol.Required("type"): "trafikverket_camera/get_cameras",
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def get_cameras(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get all cameras from trafikverket API."""
    config = hass.config_entries.async_get_entry(msg["entry_id"])
    if config is None:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_UNAUTHORIZED, "Unknown entry id"
        )
        return
    api_key: str = config.data["api_key"]
    trafikverket = Trafikverket(async_get_clientsession(hass), api_key)
    cameras = await trafikverket.async_make_request(
        "Camera",
        "1.0",
        CAMERA_INFO_REQUIRED_FIELDS,
        [
            AndFilter(
                [
                    FieldFilter(FilterOperation.EQUAL, "Type", "Trafikflödeskamera"),
                    FieldFilter(FilterOperation.EQUAL, "Active", "true"),
                    FieldFilter(FilterOperation.EQUAL, "Deleted", "false"),
                ]
            )
        ],
    )
    cameras = [CameraInfo.from_xml_node(x).__dict__ for x in cameras]
    cameras = [
        x for x in cameras if x["location"] is not None and x["description"] is not None
    ]
    connection.send_result(msg["id"], cameras)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "trafikverket_camera/remove",
        vol.Required("entry_id"): str,
        vol.Required("location"): str,
    }
)
@websocket_api.async_response
async def remove(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Remove a camera from Trafikverket camera."""
    config = hass.config_entries.async_get_entry(msg["entry_id"])
    if config is None:
        return
    all_cameras = list(config.data.get("cameras", []))
    all_cameras.remove(msg["location"])
    hass.config_entries.async_update_entry(
        config, data={**config.data, "cameras": all_cameras}
    )
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(config, platform)
    states = hass.states.async_all()
    states = [s for s in states if "trafikverket_camera" in s.entity_id]
    for state in states:
        hass.states.async_remove(state.entity_id)
    entry_id = f"{config.entry_id}/{msg['location']}"
    hass.data[DOMAIN].pop(entry_id)

    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)

    connection.send_result(msg["id"], config)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "trafikverket_camera/add",
        vol.Required("entry_id"): str,
        vol.Required("location"): str,
    }
)
@websocket_api.async_response
async def add(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add camera to the config for Trafikverket Camera."""
    config = hass.config_entries.async_get_entry(msg["entry_id"])
    if config is None:
        return
    all_cameras = list(config.data.get("cameras", []))
    all_cameras.append(msg["location"])
    hass.config_entries.async_update_entry(
        config, data={**config.data, "cameras": all_cameras}
    )

    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(config, platform)
    coordinator = TVDataUpdateCoordinator(hass, config, msg["location"])
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        connection.send_error(
            msg["id"],
            websocket_api.const.ERR_NOT_SUPPORTED,
            f"Could not add camera {msg['location']}",
        )
        return
    hass.data.setdefault(DOMAIN, {})[
        f"{config.entry_id}/{msg['location']}"
    ] = coordinator

    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)

    connection.send_result(msg["id"], config)
