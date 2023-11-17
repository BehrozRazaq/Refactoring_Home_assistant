"""Module for identifying cars."""
# import cv2
import numpy as np


class CarRectangle:
    """Rectangle representing where the model think there is a car."""

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Create a data type for car rectangle.

        (x1, y1) upper left corner
        (x2, y2) lower right corner.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class CarIdentifier:
    """Class for identifying cars based on image bytes."""

    def get_cars(self, image: bytes | None) -> list[CarRectangle]:
        """image: Bytes of the image to find cars from."""
        np.array(image)

        # image_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2GRAY)
        # image_arr = cv2.GaussianBlur(image_arr, (5, 5), 0)
        # image_arr = cv2.dilate(blur, np.ones((3, 3)))
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        # image_arr = cv2.morphologyEx(image_arr, cv2.MORPH_CLOSE, kernel)

        # car_cascade = cv2.CascadeClassifier(car_cascade_src)
        # cars = car_cascade.detectMultiScale(image_arr, 1.1, 1)

        car_rectangles: list[CarRectangle] = []
        # for x1, y1, x2, y2 in cars:
        #    car_rectangles.append(CarRectangle(x1, y1, x2, y2))
        return car_rectangles
