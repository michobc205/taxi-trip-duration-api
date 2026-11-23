"""Study: do the hour and the weekday help the model?

It trains four random forests on January (same settings as the baseline in
src/train.py): the baseline with 3 inputs, plus the pickup hour, plus the
pickup weekday, and plus both. Each model is tested on the January validation
rides and on all cleaned February rides. It does not use MLflow, so the
registered model and the API are not changed.

Run: uv run python -m src.study_time_features
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

from src.prepare_data import load_clean_data
from src.train import FEATURES, RANDOM_STATE, RF_PARAMS, SAMPLE_SIZE, TARGET, TEST_SIZE

JAN_PATH = "data/yellow_tripdata_2025-01.parquet"
FEB_PATH = "data/yellow_tripdata_2025-02.parquet"
MODELS = {
    "baseline (3 inputs)": FEATURES,
    "+ hour": FEATURES + ["pickup_hour"],
    "+ weekday": FEATURES + ["pickup_weekday"],
    "+ hour + weekday": FEATURES + ["pickup_hour", "pickup_weekday"],
}
PARTS_OF_DAY = ["night 0-5", "morning 6-9", "midday 10-15", "evening 16-19", "late 20-23"]


def add_time(df):
    df = df.copy()
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour.astype("int64")
    df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.day_of_week.astype("int64")  # Monday = 0
    return df


def part_of_day(hours):
    return pd.cut(hours, bins=[0, 6, 10, 16, 20, 24], right=False, labels=PARTS_OF_DAY)


def main():
    jan = add_time(load_clean_data(JAN_PATH, "2025-01"))
    feb = add_time(load_clean_data(FEB_PATH, "2025-02"))
    train_df, val_df = train_test_split(jan, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    sample = train_df.sample(min(SAMPLE_SIZE, len(train_df)), random_state=RANDOM_STATE)
    print("training rides used:", len(sample))

    feb_pred = {}
    for name, cols in MODELS.items():
        types = {c: ("float64" if c == "trip_distance" else "int64") for c in cols}
        model = RandomForestRegressor(n_jobs=-1, random_state=RANDOM_STATE, **RF_PARAMS)
        model.fit(sample[cols].astype(types), sample[TARGET])
        for set_name, d in [("January validation", val_df), ("February", feb)]:
            pred = model.predict(d[cols].astype(types))
            rmse = root_mean_squared_error(d[TARGET], pred)
            mae = mean_absolute_error(d[TARGET], pred)
            print(f"{name:20} {set_name:18} rides={len(d):8d}  rmse={rmse:.4f}  mae={mae:.4f}")
            if set_name == "February":
                feb_pred[name] = pred
        if name == "+ hour + weekday":
            imp = {c: round(float(v), 3) for c, v in zip(cols, model.feature_importances_)}
            print("how much each input is used (full model):", imp)

    print("February, error by part of the day (rmse):")
    parts = part_of_day(feb["pickup_hour"])
    for part in PARTS_OF_DAY:
        m = (parts == part).to_numpy()
        base = root_mean_squared_error(feb.loc[m, TARGET], feb_pred["baseline (3 inputs)"][m])
        full = root_mean_squared_error(feb.loc[m, TARGET], feb_pred["+ hour + weekday"][m])
        print(f"  {part:14} rides={int(m.sum()):8d}  baseline={base:.4f}  hour+weekday={full:.4f}")


if __name__ == "__main__":
    main()
