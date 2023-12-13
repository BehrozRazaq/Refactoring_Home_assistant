"""The test for the Trafikverket Camera coordinator."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from pytrafikverket.exceptions import (
    InvalidAuthentication,
    MultipleCamerasFound,
    NoCameraFound,
    UnknownError,
)

from homeassistant import config_entries
from homeassistant.components.trafikverket_camera.const import DOMAIN, TrafficMeasure
from homeassistant.components.trafikverket_camera.coordinator import (
    CameraData,
    TVDataUpdateCoordinator,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from . import ENTRY_CONFIG

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


async def test_coordinator(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    get_camera: CameraData,
) -> None:
    """Test the Trafikverket Camera coordinator."""
    aioclient_mock.get(
        "https://www.testurl.com/test_photo.jpg?type=fullsize",
        content=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00x\x00x\x00\x00\xff\xe1\x00"Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x01\x01\x12\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\xff\xdb\x00C\x00\x02\x01\x01\x02\x01\x01\x02\x02\x02\x02\x02\x02\x02\x02\x03\x05\x03\x03\x03\x03\x03\x06\x04\x04\x03\x05\x07\x06\x07\x07\x07\x06\x07\x07\x08\t\x0b\t\x08\x08\n\x08\x07\x07\n\r\n\n\x0b\x0c\x0c\x0c\x0c\x07\t\x0e\x0f\r\x0c\x0e\x0b\x0c\x0c\x0c\xff\xdb\x00C\x01\x02\x02\x02\x03\x03\x03\x06\x03\x03\x06\x0c\x08\x07\x08\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x00\x0f\x00\x10\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfb\x87\xe2\x0f\xc7O\x8f\x9a\xdf\x88?h\xcd\x1fI\xd3a\xf1\x17\x83t\xdb\x8dF\xcfQ\x93Ta\x1bhV\x1bnUZ\xd4\x19c\xc96\xeb\xbf\x01d\xce\xd4m\xb9\x7f\x9f\xdb\xff\x00`\x0f\x19\xea\xde\x0c\xfd\x8b\xfe\x0f\x9b=&mSL\xd55K\xdd;R6\xf0K5\xc5\x9a\xcb}v"\x98\x05R\xa2$\x93o\x98\xceB\xa2\x12A$\x00~\xa5\xbb\xb4\x8e\xf6\xdaHf\x8a9\xa1\x99JI\x1b\xa8e\x91H\xc1\x04\x1e\x08#\x8c\x1a\xf9\xf3\xf6\x97\xfd\x9f<Q\xad\xfcN\xf8 \xde\x00\xb3\xb7\xd2|+\xe0\xbdt\xdc\xea\xf6v3\xa5\x8c\x10[y\x96\xed\x91\x12\x95\x0c6$\xeb\xb5A?\xbd\xc60\xcc@\x07\xff\xd9',
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data=ENTRY_CONFIG,
        entry_id="1",
        unique_id="123",
        title="Test location",
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.trafikverket_camera.coordinator.TrafikverketCamera.async_get_camera",
        return_value=get_camera,
    ) as mock_data:
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_data.assert_called_once()
        state1 = hass.states.get("camera.test_location")
        assert state1.state == "idle"


@pytest.mark.parametrize(
    ("sideeffect", "p_error", "entry_state"),
    [
        (
            InvalidAuthentication,
            ConfigEntryAuthFailed,
            config_entries.ConfigEntryState.SETUP_ERROR,
        ),
        (
            NoCameraFound,
            UpdateFailed,
            config_entries.ConfigEntryState.SETUP_RETRY,
        ),
        (
            MultipleCamerasFound,
            UpdateFailed,
            config_entries.ConfigEntryState.SETUP_RETRY,
        ),
        (
            UnknownError,
            UpdateFailed,
            config_entries.ConfigEntryState.SETUP_RETRY,
        ),
    ],
)
async def test_coordinator_failed_update(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    get_camera: CameraData,
    sideeffect: str,
    p_error: Exception,
    entry_state: str,
    mock_database: str,
) -> None:
    """Test the Trafikverket Camera coordinator."""
    aioclient_mock.get(
        "https://www.testurl.com/test_photo.jpg?type=fullsize", content=b"0123456789"
    )

    ENTRY_CONFIG["db"] = mock_database
    entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data=ENTRY_CONFIG,
        entry_id="1",
        unique_id="123",
        title="Test location",
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.trafikverket_camera.coordinator.TrafikverketCamera.async_get_camera",
        side_effect=sideeffect,
    ) as mock_data:
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    mock_data.assert_called_once()
    state = hass.states.get("camera.test_location")
    assert state is None
    assert entry.state == entry_state


async def test_coordinator_failed_get_image(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    get_camera: CameraData,
    mock_database: str,
) -> None:
    """Test the Trafikverket Camera coordinator."""
    aioclient_mock.get(
        "https://www.testurl.com/test_photo.jpg?type=fullsize", status=404
    )

    ENTRY_CONFIG["db"] = mock_database
    entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data=ENTRY_CONFIG,
        entry_id="1",
        unique_id="123",
        title="Test location",
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.trafikverket_camera.coordinator.TrafikverketCamera.async_get_camera",
        return_value=get_camera,
    ) as mock_data:
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    mock_data.assert_called_once()
    state = hass.states.get("camera.test_location")
    assert state is None
    assert entry.state is config_entries.ConfigEntryState.SETUP_RETRY


class MockStatisticsHandler:
    """Mock Statistics handler."""

    statistics: list[tuple[str, int]]

    def __init__(self) -> None:
        """Location -> which location is used for the trafikverket camera."""
        self.statistics = []

    def get_data(self) -> list[tuple[str, int]]:
        """Retrieve all statistics data for a location."""
        return self.statistics


async def test_traffic_measure(hass: HomeAssistant, mock_database: str) -> None:
    """Test traffic measure."""
    location = "location"  # is removed in calculate_traffic_measure()

    ENTRY_CONFIG["db"] = mock_database
    entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data=ENTRY_CONFIG,
        entry_id="1",
        unique_id="123",
        title="Test location",
    )
    coordinator = TVDataUpdateCoordinator(hass, entry, location)
    coordinator._statistics_handler = MockStatisticsHandler()

    coordinator._statistics_handler.statistics = [
        (location, 1),
        (location, 2),
        (location, 2),
        (location, 3),
        (location, 3),
        (location, 3),
        (location, 4),
        (location, 4),
        (location, 5),
        (location, 6),
        (location, 10),
        (location, 10),
    ]
    assert coordinator.calculate_traffic_measure(-1) == TrafficMeasure.Unknown

    coordinator._statistics_handler.statistics = [
        (location, 1),
        (location, 1),
        (location, 3),
        (location, 3),
    ]
    assert coordinator.calculate_traffic_measure(1) == TrafficMeasure.Low
    assert coordinator.calculate_traffic_measure(2) == TrafficMeasure.Medium

    coordinator._statistics_handler.statistics = [
        (location, 1),
        (location, 1),
        (location, 2),
        (location, 2),
        (location, 2),
        (location, 2),
        (location, 5),
        (location, 5),
        (location, 6),
    ]
    assert coordinator.calculate_traffic_measure(4) == TrafficMeasure.Medium
    assert coordinator.calculate_traffic_measure(5) == TrafficMeasure.High
    assert coordinator.calculate_traffic_measure(6) == TrafficMeasure.Critical
    assert coordinator.calculate_traffic_measure(100) == TrafficMeasure.Critical
