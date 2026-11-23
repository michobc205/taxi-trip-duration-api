"""Tests for the four cleaning rules in src/prepare_data.py.

Each test writes a tiny raw file, so no real taxi data is needed.
"""
import pandas as pd
import pytest

from src.prepare_data import load_clean_data


def make_file(tmp_path, rides):
    """Write a small raw file. Each ride is (pickup time, minutes, distance in miles)."""
    rows = []
    for pickup, minutes, distance in rides:
        start = pd.Timestamp(pickup)
        rows.append(
            {
                "tpep_pickup_datetime": start,
                "tpep_dropoff_datetime": start + pd.Timedelta(minutes=minutes),
                "trip_distance": distance,
                "PULocationID": 161,
                "DOLocationID": 236,
            }
        )
    path = tmp_path / "rides.parquet"
    pd.DataFrame(rows).to_parquet(path)
    return path


JAN = "2025-01-10 10:00"

CASES = [
    pytest.param((JAN, 20, 5.0), True, id="normal ride"),
    pytest.param((JAN, 1, 0.2), True, id="exactly 1 minute is kept"),
    pytest.param((JAN, 60, 10.0), True, id="exactly 60 minutes is kept"),
    pytest.param((JAN, 6, 4.9), True, id="49 mph is kept"),
    pytest.param(("2025-01-01 00:00", 20, 5.0), True, id="first minute of January is kept"),
    pytest.param(("2025-01-31 23:59", 20, 5.0), True, id="last minute of January is kept"),
    pytest.param((JAN, 0.5, 0.1), False, id="under 1 minute is removed"),
    pytest.param((JAN, 61, 10.0), False, id="over 60 minutes is removed"),
    pytest.param((JAN, -5, 3.0), False, id="drop-off before pickup is removed"),
    pytest.param((JAN, 20, 0.0), False, id="distance 0 is removed"),
    pytest.param((JAN, 10, 9.0), False, id="54 mph is removed"),
    pytest.param(("2024-12-31 23:50", 20, 5.0), False, id="pickup in December is removed"),
    pytest.param(("2025-02-01 00:00", 20, 5.0), False, id="pickup in February is removed"),
]


@pytest.mark.parametrize("ride, kept", CASES)
def test_cleaning_rule(tmp_path, ride, kept):
    path = make_file(tmp_path, [ride])
    assert (len(load_clean_data(path)) == 1) is kept


def test_all_rules_together(tmp_path):
    rides = [case.values[0] for case in CASES]
    expected = sum(case.values[1] for case in CASES)
    path = make_file(tmp_path, rides)
    assert len(load_clean_data(path)) == expected


def test_duration_column_is_in_minutes(tmp_path):
    path = make_file(tmp_path, [(JAN, 20, 5.0)])
    clean = load_clean_data(path)
    assert clean["duration"].iloc[0] == pytest.approx(20.0)


def test_month_setting(tmp_path):
    path = make_file(tmp_path, [("2025-01-10 10:00", 20, 5.0), ("2025-02-10 10:00", 25, 6.0)])
    january = load_clean_data(path)
    february = load_clean_data(path, month="2025-02")
    assert list(january["tpep_pickup_datetime"].dt.month) == [1]
    assert list(february["tpep_pickup_datetime"].dt.month) == [2]
