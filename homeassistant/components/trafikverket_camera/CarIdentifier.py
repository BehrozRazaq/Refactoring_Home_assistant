from abc import abstractmethod


class CarRectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class CarIdentifier:

    @abstractmethod
    def get_cars(self, image: bytes | None) -> list[CarRectangle]:  # todo this looks bad, maybe fix?
        pass


class DummyAI(CarIdentifier):

    def get_cars(self, image: bytes | None) -> list[CarRectangle]:
        return [CarRectangle(0, 1, 1, 2), CarRectangle(2, 2, 3, 3), CarRectangle(1, 1, 2, 2)]
