"""Data preparation for the taxi trip duration project."""
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/yellow_tripdata_2025-01.parquet")
COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
]
MIN_MINUTES = 1
MAX_MINUTES = 60
MAX_MPH = 50  # average speed of a ride; the city default limit is 25 mph


def load_clean_data(path=DATA_PATH):
    """Load the raw file and keep only the rides that pass the cleaning rules."""
    df = pd.read_parquet(path, columns=COLUMNS)
    df["duration"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60
    in_january = (df["tpep_pickup_datetime"] >= "2025-01-01") & (
        df["tpep_pickup_datetime"] < "2025-02-01"
    )
    ok_duration = df["duration"].between(MIN_MINUTES, MAX_MINUTES)
    ok_distance = df["trip_distance"] > 0
    mph = df["trip_distance"] / (df["duration"] / 60)
    ok_speed = mph <= MAX_MPH
    return df[in_january & ok_duration & ok_distance & ok_speed].reset_index(drop=True)


if __name__ == "__main__":
    import pyarrow.parquet as pq

    raw_rows = pq.ParquetFile(DATA_PATH).metadata.num_rows
    clean = load_clean_data()
    print("raw rows  :", raw_rows)
    print("kept rows :", len(clean))
    print("kept share:", round(100 * len(clean) / raw_rows, 2), "%")
    print("duration median:", round(clean["duration"].median(), 2), "minutes")
    print("distance max:", clean["trip_distance"].max(), "miles")
    print("speed max   :", round((clean["trip_distance"] / (clean["duration"] / 60)).max(), 2), "mph")
