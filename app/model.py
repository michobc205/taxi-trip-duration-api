"""Load the registered model from MLflow and use it for one ride."""
import os

import mlflow
import pandas as pd

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = os.getenv("REGISTERED_MODEL_NAME", "taxi-trip-duration-rf")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "production")


def load_model():
    """Load the model that carries the alias. Called once, when the API starts."""
    mlflow.set_tracking_uri(TRACKING_URI)
    return mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@{MODEL_ALIAS}")


def predict_duration(model, ride):
    """Return the predicted duration in minutes, rounded to 2 decimals."""
    row = pd.DataFrame(
        {
            "PULocationID": [ride.PULocationID],
            "DOLocationID": [ride.DOLocationID],
            "trip_distance": [ride.trip_distance],
        }
    ).astype({"PULocationID": "int64", "DOLocationID": "int64", "trip_distance": "float64"})
    return round(float(model.predict(row)[0]), 2)
