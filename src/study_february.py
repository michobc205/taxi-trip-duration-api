"""Study: test the January model on February (a split by time).

It trains the same random forest as src/train.py on January, then tests it on
the January validation rides and on all cleaned February rides. It does not
use MLflow, so the registered model and the API are not changed.

Run: uv run python -m src.study_february
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

from src.prepare_data import load_clean_data
from src.train import FEATURES, RANDOM_STATE, RF_PARAMS, SAMPLE_SIZE, TARGET, TEST_SIZE

JAN_PATH = "data/yellow_tripdata_2025-01.parquet"
FEB_PATH = "data/yellow_tripdata_2025-02.parquet"
TYPES = {"PULocationID": "int64", "DOLocationID": "int64", "trip_distance": "float64"}


def main():
    jan = load_clean_data(JAN_PATH, "2025-01")
    feb = load_clean_data(FEB_PATH, "2025-02")
    train_df, val_df = train_test_split(jan, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    sample = train_df.sample(min(SAMPLE_SIZE, len(train_df)), random_state=RANDOM_STATE)
    model = RandomForestRegressor(n_jobs=-1, random_state=RANDOM_STATE, **RF_PARAMS)
    model.fit(sample[FEATURES].astype(TYPES), sample[TARGET])
    naive_value = train_df[TARGET].mean()
    print("training rides used:", len(sample), "| naive answer (January mean):", round(naive_value, 2), "minutes")
    for name, d in [("January validation", val_df), ("February (never seen)", feb)]:
        pred = model.predict(d[FEATURES].astype(TYPES))
        rmse = root_mean_squared_error(d[TARGET], pred)
        mae = mean_absolute_error(d[TARGET], pred)
        naive = root_mean_squared_error(d[TARGET], np.full(len(d), naive_value))
        print(f"{name:22} rides={len(d):8d}  rmse={rmse:.4f}  mae={mae:.4f}  naive_rmse={naive:.4f}  median_duration={d[TARGET].median():.2f}")


if __name__ == "__main__":
    main()
