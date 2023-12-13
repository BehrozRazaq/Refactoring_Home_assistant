"""Functions to interact with an SQLite database for traffic data."""
import logging
import os
import sqlite3


class Operations:
    """Database interface."""

    def __init__(self, config_dir: str) -> None:
        """Create an empty table if traffic_amount is not present."""
        self.database_path = os.path.join(config_dir, "home-assistant_v2.db")
        self._logger = logging.getLogger(__name__)
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='traffic_amount'"
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        "CREATE TABLE traffic_amount (location VARCHAR(255), time DATETIME, nr_cars INTEGER NOT NULL)"
                    )
                    conn.commit()
        except sqlite3.Error as e:
            err_msg = f"SQLite error: {e}"
            self._logger.error(err_msg)

    def insert_traffic_entry(self, location: str, time: str, nr_cars: int) -> None:
        """Insert a new traffic entry into the database.

        Args:
            location: The location of the camera.
            time: The timestamp of the traffic entry.
            nr_cars: The number of cars at the given location and time.
        """
        if nr_cars < 0:
            raise ValueError("Cannot have negative amount of cars")
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.cursor()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO traffic_amount (location, time, nr_cars) VALUES (?,?,?)",
                    (location, time, nr_cars),
                )
                conn.commit()
        except sqlite3.Error as e:
            err_msg = f"SQLite error: {e}"
            self._logger.error(err_msg)

    def query_time_and_cars_by_location(self, location: str) -> list[tuple[str, int]]:
        """Query the time and number of cars for a specific location.

        Args:
            location: The location of the camera.

        Returns:
            A list of tuples containing the time and number of cars at the specified location.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT time, nr_cars FROM traffic_amount WHERE location = ?",
                    (location,),
                )
                entries = cursor.fetchall()
            if not entries:
                return []
            return entries
        except sqlite3.Error as e:
            err_msg = f"SQLite error: {e}"
            self._logger.error(err_msg)
        return []

    def query_time_and_cars_by_location_and_time(
        self, location: str, start_time: str, end_time: str
    ) -> list[tuple[str, int]]:
        """Query the time and number of cars for a given location and time span.

        Args:
            location: The location of the camera.
            start_time: The start of the time span.
            end_time: The end of the time span.

        Returns:
        A list of tuples containing the time and number of cars at the specified location and time span.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT time, nr_cars
                    FROM traffic_amount
                    WHERE location = ? AND time >= ? AND time <= ?
                    """,
                    (location, start_time, end_time),
                )
                data = cursor.fetchall()
        except sqlite3.Error as e:
            err_msg = f"SQLite error: {e}"
            self._logger.error(err_msg)
        return data
