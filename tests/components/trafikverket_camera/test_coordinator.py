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
        "https://www.testurl.com/test_photo.jpg?type=fullsize", content=b"0123456789"
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
    coordinator = TVDataUpdateCoordinator(hass, entry)
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
