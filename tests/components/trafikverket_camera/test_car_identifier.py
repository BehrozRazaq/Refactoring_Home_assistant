"""The tests for the car identifier file."""
from homeassistant.components.trafikverket_camera.car_identifier import CarRectangle, CarIdentifier

def test_car_rectangle_to_dict() -> None:
    dict = CarRectangle(1, 0, 5, 50).to_dict()
    assert dict["x1"] == 1
    assert dict["y1"] == 0
    assert dict["x2"] == 5
    assert dict["y2"] == 50


def test_car_identifier_no_image() -> None:
    identifier = CarIdentifier()
    assert identifier.get_cars(None) == []
