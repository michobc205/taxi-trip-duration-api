"""Study: what happens when the training rides are limited by average speed?

It trains five random forests on January (same settings as the baseline in
src/train.py). Each one may only train on rides with an average speed up to a
limit: 25, 30, 35, 40 or 50 mph. The 50 mph model is the baseline, because the
cleaning rules already stop at 50 mph. All five are tested on the same rides:
the January validation rides (split into rides up to 25 mph and rides over
25 mph) and all cleaned February rides. It does not use MLflow, so the
registered model and the API are not changed.

Run: uv run python -m src.study_speed_limit
"""
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

from src.prepare_data import load_clean_data
from src.train import FEATURES, RANDOM_STATE, RF_PARAMS, SAMPLE_SIZE, TARGET, TEST_SIZE

JAN_PATH = "data/yellow_tripdata_2025-01.parquet"
FEB_PATH = "data/yellow_tripdata_2025-02.parquet"
LIMITS = [25, 30, 35, 40, 50]
TYPES = {"PULocationID": "int64", "DOLocationID": "int64", "trip_distance": "float64"}


def add_speed(df):
    df = df.copy()
    df["mph"] = df["trip_distance"] / (df["duration"] / 60)
    return df


def main():
    jan = add_speed(load_clean_data(JAN_PATH, "2025-01"))
    feb = add_speed(load_clean_data(FEB_PATH, "2025-02"))
    train_df, val_df = train_test_split(jan, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    tests = {
        "Jan up to 25 mph": val_df[val_df["mph"] <= 25],
        "Jan over 25 mph": val_df[val_df["mph"] > 25],
        "Jan all": val_df,
        "Feb all": feb,
    }
    print("test sets (rides):", {k: len(v) for k, v in tests.items()})
    print("share of January validation rides over 25 mph:",
          round(100 * len(tests["Jan over 25 mph"]) / len(val_df), 2), "%")
    print()
    print(f"{'limit':>6} {'rides allowed':>14} {'rmse up to 25':>14} {'rmse over 25':>13} {'rmse Jan all':>13} {'rmse Feb all':>13} {'mae Feb all':>12}")
    for limit in LIMITS:
        allowed = train_df[train_df["mph"] <= limit]
        sample = allowed.sample(min(SAMPLE_SIZE, len(allowed)), random_state=RANDOM_STATE)
        model = RandomForestRegressor(n_jobs=-1, random_state=RANDOM_STATE, **RF_PARAMS)
        model.fit(sample[FEATURES].astype(TYPES), sample[TARGET])
        rmse = {}
        for name, d in tests.items():
            pred = model.predict(d[FEATURES].astype(TYPES))
            rmse[name] = root_mean_squared_error(d[TARGET], pred)
            if name == "Feb all":
                mae_feb = mean_absolute_error(d[TARGET], pred)
        print(f"{limit:>6} {len(allowed):>14d} {rmse['Jan up to 25 mph']:>14.4f} {rmse['Jan over 25 mph']:>13.4f} {rmse['Jan all']:>13.4f} {rmse['Feb all']:>13.4f} {mae_feb:>12.4f}")


if __name__ == "__main__":
    main()
