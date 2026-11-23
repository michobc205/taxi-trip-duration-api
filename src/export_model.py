"""Export the registered model (the one with the alias) to a local folder.

The Docker image copies this folder, so the container needs no MLflow server.
MLflow must be running when you run this.

Run: uv run python -m src.export_model
"""
import os
import shutil

import mlflow

from app.model import MODEL_ALIAS, MODEL_NAME, TRACKING_URI

OUT_DIR = os.getenv("EXPORT_DIR", "model")


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    path = mlflow.artifacts.download_artifacts(artifact_uri=uri, dst_path=OUT_DIR)
    print("exported", uri)
    print("to folder:", path)
    print("files    :", sorted(os.listdir(path)))


if __name__ == "__main__":
    main()
