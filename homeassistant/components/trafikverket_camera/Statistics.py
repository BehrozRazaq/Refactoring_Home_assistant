"""Module for statistics of cars for Trafikverket."""
from dataclasses import dataclass


@dataclass
class Entry:
    """An entity for the database for car statistics."""

    location: str
    time: int
    nr_cars: int


class StatisticsHandler:
    """Handler for the database."""

    statistics: list[Entry]

    def __init__(self, location: str) -> None:
        """Based on location, creates a handler for the database."""
        self.statistics = []

    def new_entry(self, location: str, time: int, nr_cars: int) -> None:
        """Add new entry to the database."""
        self.statistics.append(Entry(location, time, nr_cars))

    def get_data(self) -> list[Entry]:
        """Get all data from the database."""
        return self.statistics
