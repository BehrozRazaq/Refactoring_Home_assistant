"""Services for the Plex integration."""
import json
import logging
import typing

from plexapi.exceptions import NotFound
import voluptuous as vol
from yarl import URL

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    PLEX_UPDATE_PLATFORMS_SIGNAL,
    PLEX_URI_SCHEME,
    SERVERS,
    SERVICE_REFRESH_LIBRARY,
    SERVICE_SCAN_CLIENTS,
)
from .errors import MediaNotFound
from .helpers import get_plex_data
from .models import PlexMediaSearchResult
from .server import PlexServer

REFRESH_LIBRARY_SCHEMA = vol.Schema(
    {vol.Optional("server_name"): str, vol.Required("library_name"): str}
)

_LOGGER = logging.getLogger(__package__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Plex component."""

    async def async_refresh_library_service(service_call: ServiceCall) -> None:
        await hass.async_add_executor_job(refresh_library, hass, service_call)

    async def async_scan_clients_service(_: ServiceCall) -> None:
        _LOGGER.warning(
            "This service is deprecated in favor of the scan_clients button entity."
            " Service calls will still work for now but the service will be removed in"
            " a future release"
        )
        for server_id in get_plex_data(hass)[SERVERS]:
            async_dispatcher_send(hass, PLEX_UPDATE_PLATFORMS_SIGNAL.format(server_id))

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_LIBRARY,
        async_refresh_library_service,
        schema=REFRESH_LIBRARY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SCAN_CLIENTS, async_scan_clients_service
    )


def refresh_library(hass: HomeAssistant, service_call: ServiceCall) -> None:
    """Scan a Plex library for new and updated media."""
    plex_server_name = service_call.data.get("server_name")
    library_name = service_call.data["library_name"]

    plex_server = get_plex_server(hass, plex_server_name)

    try:
        library = plex_server.library.section(title=library_name)
    except NotFound:
        _LOGGER.error(
            "Library with name '%s' not found in %s",
            library_name,
            [x.title for x in plex_server.library.sections()],
        )
        return

    _LOGGER.debug("Scanning %s for new and updated media", library_name)
    library.update()


def get_plex_server(
    hass: HomeAssistant,
    plex_server_name: str | None = None,
    plex_server_id: str | None = None,
) -> PlexServer:
    """Retrieve a configured Plex server by name."""
    if DOMAIN not in hass.data:
        raise HomeAssistantError("Plex integration not configured")
    servers: dict[str, PlexServer] = get_plex_data(hass)[SERVERS]
    if not servers:
        raise HomeAssistantError("No Plex servers available")

    if plex_server_id:
        return servers[plex_server_id]

    plex_servers = servers.values()
    if plex_server_name:
        plex_server = next(
            (x for x in plex_servers if x.friendly_name == plex_server_name), None
        )
        if plex_server is not None:
            return plex_server
        friendly_names = [x.friendly_name for x in plex_servers]
        raise HomeAssistantError(
            f"Requested Plex server '{plex_server_name}' not found in {friendly_names}"
        )

    if len(plex_servers) == 1:
        return next(iter(plex_servers))

    friendly_names = [x.friendly_name for x in plex_servers]
    raise HomeAssistantError(
        "Multiple Plex servers configured, choose with 'plex_server' key:"
        f" {friendly_names}"
    )


def _handle_standard_payloads(
    hass: HomeAssistant, plex_url: typing.Any, plex_server: PlexServer | None
):
    # Handle standard media_browser payloads
    if plex_url.name:
        server_id = plex_url.host
        plex_server = get_plex_server(hass, plex_server_id=server_id)
        if len(plex_url.parts) == 2:
            if plex_url.name == "search":
                return {}, plex_server
            return int(plex_url.name), plex_server
        # For "special" items like radio stations
        return plex_url.path, plex_server
    # Handle legacy payloads without server_id in URL host position
    if plex_url.host == "search":  # noqa: PLR5501
        return {}, None
    return int(plex_url.host), None  # type: ignore[arg-type]


def _handle_playqueue_media(
    playqueue_id: "int | typing.Any",
    supports_playqueues: bool,
    plex_server: PlexServer | None,
    content: "dict[str, int] | typing.Any",
):
    if not supports_playqueues:
        raise HomeAssistantError("Plex playqueues are not supported on this device")
    try:
        playqueue = plex_server.get_playqueue(playqueue_id)
    except NotFound as err:
        raise MediaNotFound(f"PlayQueue '{playqueue_id}' could not be found") from err
    return PlexMediaSearchResult(playqueue, content)


def _handle_content_as_media_or_playqueue(
    content_type: str,
    search_query: dict[str, int] | typing.Any,
    supports_playqueues: bool,
    shuffle: int | typing.Any,
    plex_server: PlexServer | None,
    content: dict[str, int] | typing.Any,
):
    media = plex_server.lookup_media(content_type, **search_query)
    if supports_playqueues and (isinstance(media, list) or shuffle):
        playqueue = plex_server.create_playqueue(
            media, includeRelated=0, shuffle=shuffle
        )
        return PlexMediaSearchResult(playqueue, content)

    return PlexMediaSearchResult(media, content)


def process_plex_payload(
    hass: HomeAssistant,
    content_type: str,
    content_id: str,
    default_plex_server: PlexServer | None = None,
    supports_playqueues: bool = True,
) -> PlexMediaSearchResult:
    """Look up Plex media using media_player.play_media service payloads."""
    plex_server = default_plex_server
    extra_params = {}

    if content_id.startswith(PLEX_URI_SCHEME + "{"):
        # Handle the special payload of 'plex://{<json>}'
        content_id = content_id.removeprefix(PLEX_URI_SCHEME)
        content = json.loads(content_id)
    elif content_id.startswith(PLEX_URI_SCHEME):
        plex_url = URL(content_id)
        content, potential_plex_server = _handle_standard_payloads(
            hass, plex_url, plex_server
        )
        plex_server = potential_plex_server if potential_plex_server else plex_server
        extra_params = dict(plex_url.query)
    else:
        content = json.loads(content_id)

    if isinstance(content, dict):
        if plex_server_name := content.pop("plex_server", None):
            plex_server = get_plex_server(hass, plex_server_name)

    if not plex_server:
        plex_server = get_plex_server(hass)

    if content_type == "station":
        if not supports_playqueues:
            raise HomeAssistantError("Plex stations are not supported on this device")
        playqueue = plex_server.create_station_playqueue(content)
        return PlexMediaSearchResult(playqueue)

    if isinstance(content, int):
        content = {"plex_key": content}
        content_type = DOMAIN

    content.update(extra_params)

    if playqueue_id := content.pop("playqueue_id", None):
        return _handle_playqueue_media(
            playqueue_id, supports_playqueues, plex_server, content
        )

    search_query = content.copy()
    shuffle = search_query.pop("shuffle", 0)

    # Remove internal kwargs before passing copy to plexapi
    for internal_key in ("resume", "offset"):
        search_query.pop(internal_key, None)

    return _handle_content_as_media_or_playqueue(
        content_type, search_query, supports_playqueues, shuffle, plex_server, content
    )
