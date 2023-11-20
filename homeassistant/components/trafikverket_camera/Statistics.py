import traffic_data_operations


class StatisticsHandler:
    statistics: list[tuple[str, int]]

    def __init__(self, location):
        self.statistics = traffic_data_operations.query_time_and_cars_by_location(location)

    def new_entry(self, location: str, time: str, nr_cars: int):
        self.statistics.append((time, nr_cars))
        traffic_data_operations.insert_traffic_entry(location, time, nr_cars)

    def get_data(self) -> list[tuple[str, int]]:
        return self.statistics
