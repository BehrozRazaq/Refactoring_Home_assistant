"""Module for representing ai model and data it creates."""
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


class CarRectangle:
    """Representing the rectangle of the car found."""

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Take in pixel position for two opposite corners.

        (x1, y1) -> Upper left corner.
        (x2, y2) -> lower left corner.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def to_dict(self) -> dict[str, int]:
        """CarRectangle as a dictionary for converting to JSON data."""
        return {
            "x1": int(self.x1),
            "x2": int(self.x2),
            "y1": int(self.y1),
            "y2": int(self.y2),
        }


class CarIdentifier:
    """Interface for the AI model."""

    def get_cars(self, image: BytesIO | None) -> list[CarRectangle]:
        """With given image data, spits out where the cars are placed in the image."""
        assert image
        image_arr = np.array(Image.open(image))

        image_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2GRAY)
        image_arr = cv2.GaussianBlur(image_arr, (5, 5), 0)
        image_arr = cv2.dilate(image_arr, np.ones((3, 3)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        image_arr = cv2.morphologyEx(image_arr, cv2.MORPH_CLOSE, kernel)

        car_cascade_src = "./homeassistant/components/trafikverket_camera/cars.xml"
        car_cascade = cv2.CascadeClassifier(car_cascade_src)
        cars = car_cascade.detectMultiScale(image_arr, 1.1, 1)

        car_rectangles = []
        for x1, y1, x2, y2 in cars:
            car_rectangles.append(CarRectangle(x1, y1, x2, y2))
        return car_rectangles
