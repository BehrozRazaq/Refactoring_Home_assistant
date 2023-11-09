class Entry:
    location: str
    time: int  # ?
    nr_cars: int


class StatisticHandler:
    statistics: list[Entry]

    def __init__(self):
        self.statistics = self.database_querier()
        # query database

    def new_entry(self, entry: Entry):
        self.statistics.append(entry)

    def database_querier(self) -> list[Entry]:
        pass
