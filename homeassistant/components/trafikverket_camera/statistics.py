"""Handles all the statistics."""
from .traffic_data_operations import Operations


class StatisticsHandler:
    """Class where data is handled for the statistics."""

    statistics: list[tuple[str, int]]

    def __init__(self, location: str, config_dir: str) -> None:
        """Location -> which location is used for the trafikverket camera."""
        self.database_connector = Operations(config_dir)
        self.statistics = self.database_connector.query_time_and_cars_by_location(
            location
        )

    def new_entry(self, location: str, time: str, nr_cars: int) -> None:
        """Save a new data point."""
        self.statistics.append((time, nr_cars))
        self.database_connector.insert_traffic_entry(location, time, nr_cars)

    def get_data(self) -> list[tuple[str, int]]:
        """Retrieve all statistics data for a location."""
        return self.statistics
