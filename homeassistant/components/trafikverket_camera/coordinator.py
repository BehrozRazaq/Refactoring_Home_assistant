"""DataUpdateCoordinator for the Trafikverket Camera integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
import logging

from pytrafikverket.exceptions import (
    InvalidAuthentication,
    MultipleCamerasFound,
    NoCameraFound,
    UnknownError,
)
from pytrafikverket.trafikverket_camera import CameraInfo, TrafikverketCamera

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .car_identifier import CarIdentifier, CarRectangle
from .const import DOMAIN, TrafficMeasure
from .statistics import StatisticsHandler
from .traffic_data_operations import Operations

_LOGGER = logging.getLogger(__name__)
TIME_BETWEEN_UPDATES = timedelta(minutes=5)


@dataclass
class CameraData:
    """Dataclass for Camera data."""

    data: CameraInfo
    image: bytes | None
    car_list: list[CarRectangle]
    traffic_measure: TrafficMeasure


@dataclass
class CameraState:
    """State of the trafikverket Camera."""

    latest_data: CameraData
    statistics: list[tuple[str, int]]


class TVDataUpdateCoordinator(DataUpdateCoordinator[CameraData]):
    """A Trafikverket Data Update Coordinator."""

    statistics: list[tuple[str, int]]
    car_rectangles: list[CarRectangle] = []
    traffic_measure = TrafficMeasure.Unknown

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, location: str) -> None:
        """Initialize the Trafikverket coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=TIME_BETWEEN_UPDATES,
        )
        self.session = async_get_clientsession(hass)
        self._camera_api = TrafikverketCamera(self.session, entry.data[CONF_API_KEY])
        self._location = location
        self._operations = Operations(hass.config.config_dir)
        self._AI = CarIdentifier()
        self._statistics_handler = StatisticsHandler(
            self._location, hass.config.config_dir
        )

    async def _async_update_data(self) -> CameraData:
        """Fetch data from Trafikverket."""
        camera_info: CameraInfo
        image: bytes | None = None
        car_list: list[CarRectangle] = []
        traffic_measure = TrafficMeasure.Unknown
        try:
            camera_info = await self._camera_api.async_get_camera(self._location)
        except (NoCameraFound, MultipleCamerasFound, UnknownError) as error:
            raise UpdateFailed from error
        except InvalidAuthentication as error:
            raise ConfigEntryAuthFailed from error

        if camera_info.photourl is None:
            return CameraData(
                data=camera_info,
                image=None,
                car_list=car_list,
                traffic_measure=traffic_measure,
            )

        image_url = camera_info.photourl
        if camera_info.fullsizephoto:
            image_url = f"{camera_info.photourl}?type=fullsize"

        async with self.session.get(image_url, timeout=10) as get_image:
            if get_image.status not in range(200, 299):
                raise UpdateFailed("Could not retrieve image")
            image_stream = BytesIO(await get_image.read())
            image = image_stream.getvalue()
            car_list = self.process_image(camera_info, image_stream)
            traffic_measure = self.calculate_traffic_measure(camera_info, len(car_list))

        camera_data = CameraData(
            data=camera_info,
            image=image,
            car_list=car_list,
            traffic_measure=traffic_measure,
        )

        self.statistics = self._statistics_handler.get_data()
        self.car_rectangles = car_list
        self.traffic_measure = traffic_measure

        return camera_data

    def process_image(
        self, camera_info: CameraInfo, image: BytesIO | None
    ) -> list[CarRectangle]:
        """Give the image to the model for prediction."""
        rectangles = self._AI.get_cars(image)
        time = str(camera_info.phototime)

        self._statistics_handler.new_entry(self._location, time, len(rectangles))
        return rectangles

    def calculate_traffic_measure(
        self, camera_info: CameraInfo, nr_cars: int
    ) -> TrafficMeasure:
        """Give a label for how much traffic there is at the moment."""
        values = [values[1] for values in self._statistics_handler.get_data()]
        values.sort()

        # if nr_cars reoccurs many times we take the middle position
        index = values.index(nr_cars) + values.count(nr_cars) / 2
        percent = index / len(values)

        if percent > 0.9:
            return TrafficMeasure.Critical
        if percent > 0.7:
            return TrafficMeasure.High
        if percent > 0.5:
            return TrafficMeasure.Medium
        return TrafficMeasure.Low
