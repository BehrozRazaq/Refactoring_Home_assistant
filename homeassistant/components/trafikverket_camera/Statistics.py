from dataclasses import dataclass


@dataclass
class Entry:
    location: str
    time: int
    nr_cars: int


class StatisticsHandler:
    statistics: list[Entry]

    def __init__(self, location):
        self.statistics = []
        #todo query database (get all entries from this camera)

    def new_entry(self, location: str, time: int, nr_cars: int):
        self.statistics.append(Entry(location, time, nr_cars))
        #todo add to database

    def get_data(self) -> list[Entry]:
        return self.statistics

