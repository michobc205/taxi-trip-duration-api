"""Train the baseline random forest and track it in MLflow."""
import os

import mlflow
import numpy as np
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

from src.prepare_data import (
    MAX_MINUTES,
    MAX_MPH,
    MIN_MINUTES,
    load_clean_data,
)

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "taxi-trip-duration")
MODEL_NAME = os.getenv("REGISTERED_MODEL_NAME", "taxi-trip-duration-rf")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "production")

FEATURES = ["PULocationID", "DOLocationID", "trip_distance"]
TARGET = "duration"
TEST_SIZE = 0.2
SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", "200000"))
RANDOM_STATE = 42
RF_PARAMS = {"n_estimators": 50, "min_samples_leaf": 20}
# MLflow saves scikit-learn models with skops, which refuses unknown types.
# A random forest holds trees of this type. We trained the model ourselves,
# so we trust exactly this one type and nothing else.
SKOPS_TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]


def main():
    df = load_clean_data()
    train_df, val_df = train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    sample = train_df.sample(min(SAMPLE_SIZE, len(train_df)), random_state=RANDOM_STATE)

    # The API receives plain JSON numbers (int64 and float64), so the model
    # is trained on exactly these types. The signature then matches.
    types = {"PULocationID": "int64", "DOLocationID": "int64", "trip_distance": "float64"}
    X_train = sample[FEATURES].astype(types)
    X_val = val_df[FEATURES].astype(types)

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name="random-forest-baseline") as run:
        mlflow.log_params(
            {
                **RF_PARAMS,
                "random_state": RANDOM_STATE,
                "test_size": TEST_SIZE,
                "sample_size": len(sample),
                "features": ",".join(FEATURES),
                "min_minutes": MIN_MINUTES,
                "max_minutes": MAX_MINUTES,
                "max_mph": MAX_MPH,
                "rows_after_cleaning": len(df),
                "train_rows": len(train_df),
                "val_rows": len(val_df),
            }
        )

        model = RandomForestRegressor(n_jobs=-1, random_state=RANDOM_STATE, **RF_PARAMS)
        model.fit(X_train, sample[TARGET])

        pred = model.predict(X_val)
        naive = np.full(len(val_df), train_df[TARGET].mean())
        rmse = root_mean_squared_error(val_df[TARGET], pred)
        metrics = {
            "rmse": rmse,
            "mae": mean_absolute_error(val_df[TARGET], pred),
            "naive_rmse": root_mean_squared_error(val_df[TARGET], naive),
        }
        mlflow.log_metrics(metrics)

        info = mlflow.sklearn.log_model(
            model,
            name="model",
            signature=infer_signature(X_val.head(5), pred[:5]),
            input_example=X_val.head(3),
            registered_model_name=MODEL_NAME,
            skops_trusted_types=SKOPS_TRUSTED_TYPES,
        )

    client = MlflowClient()
    version = max(
        int(v.version) for v in client.search_model_versions(f"name='{MODEL_NAME}'")
    )
    client.set_registered_model_alias(MODEL_NAME, MODEL_ALIAS, str(version))

    print("run_id          :", run.info.run_id)
    print("model uri       :", info.model_uri)
    print("registered as   :", MODEL_NAME, "version", version, "alias", MODEL_ALIAS)
    for key, value in metrics.items():
        print(f"{key:16}: {value:.4f}")


if __name__ == "__main__":
    main()
