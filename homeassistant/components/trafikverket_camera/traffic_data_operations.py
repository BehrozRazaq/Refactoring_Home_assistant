"""Functions to interact with an SQLite database for traffic data."""
import sqlite3

conn = sqlite3.connect("home_assistant.db")

cursor = conn.cursor()

class Operations:
    def insert_traffic_entry(location: str, time: str, nr_cars: int) -> None:
        """Insert a new traffic entry into the database.

        Args:
            location: The location of the camera.
            time: The timestamp of the traffic entry.
            nr_cars: The number of cars at the given location and time.
        """
        cursor.execute(
            "INSERT INTO traffic_amount VALUES (?,?,?)", (location, time, nr_cars)
        )


    # Function to query time and number of cars in a location
    def query_time_and_cars_by_location(location: str) -> list[tuple[str, int]]:
        """Query the time and number of cars for a specific location.

        Args:
            location: The location of the camera.

        Returns:
            A list of tuples containing the time and number of cars at the specified location.
        """
        cursor.execute("SELECT time, nr_cars FROM traffic_amount WHERE location = ?", (location,))
        entries = cursor.fetchall()
        return entries


    # Function to query time and number of cars by location and time
    def query_time_and_cars_by_location_and_time(
        location: str, start_time: str, end_time: str
    ) -> list[tuple[str, int]]:
        """Query the time and number of cars for a given location and time span.

        Args:
            location: The location of the camera.
            start_time: The start of the time span.
            end_time: The end of the time span.

        Returns:
        A list of tuples containing the time and number of cars at the specified location and time span.
        """
        cursor.execute(
            """
            SELECT time, nr_cars
            FROM traffic_amount
            WHERE location = ? AND time >= ? AND time <= ?
            """,
            (location, start_time, end_time),
        )
        data = cursor.fetchall()
        return data


    conn.close()
