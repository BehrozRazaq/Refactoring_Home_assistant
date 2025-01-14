"""Test traffic data operations."""
from pathlib import Path
import sqlite3

import pytest

from homeassistant.components.trafikverket_camera.traffic_data_operations import (
    Operations,
)


def test_insert_traffic_entry(mock_database) -> None:
    """Tests the function insert_traffic_entry."""
    default_time = "2023-01-01 12:00:00"
    default_location = "Bur nordöst"
    default_nr_cars = 10

    valid_nr_cars = [10, 100, 0, 1000]
    invalid_nr_cars = [-10, -5000]

    operations = Operations(config_dir=str(Path(mock_database).parent))

    for valid_count in valid_nr_cars:
        operations.insert_traffic_entry(default_location, default_time, valid_count)

    for invalid_count in invalid_nr_cars:
        with pytest.raises(ValueError):
            operations.insert_traffic_entry(
                default_location, default_time, invalid_count
            )

    with sqlite3.connect(mock_database) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM traffic_amount WHERE location = ?", (default_location,)
        )
        result = cursor.fetchone()

    assert isinstance(result, tuple)
    assert result is not None
    assert result[0] == default_location
    assert result[1] == default_time
    assert result[2] == default_nr_cars


def test_query_time_and_cars_by_location(mock_database) -> None:
    """Tests the function query_time_and_cars_by_location."""
    location = "test_location"
    valid_time = "2023-01-01 12:00:00"
    nr_cars = 10

    operations = Operations(config_dir=str(Path(mock_database).parent))

    with sqlite3.connect(mock_database) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO traffic_amount (location, time, nr_cars) VALUES (?, ?, ?)",
            (location, valid_time, nr_cars),
        )
        conn.commit()

    result = operations.query_time_and_cars_by_location(location)

    assert isinstance(result, list)
    assert result is not None
    assert result == [(valid_time, nr_cars)]


def test_query_time_and_cars_by_location_and_time(mock_database) -> None:
    """Tests the function query_time_and_cars_by_location_and_time."""
    location = "test_location"
    times = [
        "2023-01-01 12:00:00",
        "2023-02-01 12:00:00",
        "2023-03-01 12:00:00",
        "2023-04-01 12:00:00",
    ]
    start_time = times[0]
    end_time = times[2]
    nr_cars = 10

    operations = Operations(config_dir=str(Path(mock_database).parent))

    with sqlite3.connect(mock_database) as conn:
        cursor = conn.cursor()
        for time in times:
            cursor.execute(
                "INSERT INTO traffic_amount (location, time, nr_cars) VALUES (?, ?, ?)",
                (location, time, nr_cars),
            )
        conn.commit()

        result = operations.query_time_and_cars_by_location_and_time(
            location, start_time, end_time
        )

        assert isinstance(result, list)
        assert result is not None
        assert result == [(times[0], nr_cars), (times[1], nr_cars), (times[2], nr_cars)]
