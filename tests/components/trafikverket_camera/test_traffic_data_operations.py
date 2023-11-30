import sqlite3

import pytest

from homeassistant.components.trafikverket_camera.traffic_data_operations import (
    Operations,
)


@pytest.fixture
def setup_temporary_database(tmp_path):
    temp_db_file = tmp_path / "test_db.db"

    with sqlite3.connect(temp_db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS traffic_amount (
                location VARCHAR(255),
                time DATETIME,
                nr_cars INTEGER NOT NULL
            )
        """
        )
        conn.commit()

    return temp_db_file


def test_insert_traffic_entry(setup_temporary_database):
    location = "test_location"
    time = "2023-01-01 12:00:00"
    nr_cars = 10

    operations = Operations(db_file=setup_temporary_database)
    operations.insert_traffic_entry(location, time, nr_cars)

    with sqlite3.connect(setup_temporary_database) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traffic_amount WHERE location = ?", (location,))
        result = cursor.fetchone()

    assert isinstance(result, tuple)
    assert result is not None
    assert result[0] == location
    assert result[1] == time
    assert result[2] == nr_cars


def test_query_time_and_cars_by_location(setup_temporary_database):
    location = "test_location"
    time = "2023-01-01 12:00:00"
    nr_cars = 10

    operations = Operations(db_file=setup_temporary_database)

    with sqlite3.connect(setup_temporary_database) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO traffic_amount (location, time, nr_cars) VALUES (?, ?, ?)",
            (location, time, nr_cars),
        )
        conn.commit()

    result = operations.query_time_and_cars_by_location(location)

    assert isinstance(result, list)
    assert result is not None
    assert result == [(time, nr_cars)]


def test_query_time_and_cars_by_location_and_time():
    # TODO
    pass
