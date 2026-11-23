"""Tests for predict_duration in app/model.py, with a fake model."""
from types import SimpleNamespace

import app.model as model_module
from app.model import predict_duration
from app.schemas import TaxiRide

RIDE = TaxiRide(ride_id="ride-101", PULocationID=161, DOLocationID=236, trip_distance=3.5)


def test_answer_is_rounded_to_two_decimals(fake_model):
    fake_model.answer = 20.4849
    assert predict_duration(fake_model, RIDE) == 20.48


def test_answer_is_a_plain_float(fake_model):
    assert isinstance(predict_duration(fake_model, RIDE), float)


def fake_mlflow(seen):
    """A tiny stand-in for the mlflow module that only records what is loaded."""
    return SimpleNamespace(
        set_tracking_uri=lambda uri: None,
        pyfunc=SimpleNamespace(load_model=lambda uri: seen.append(uri)),
    )


def test_model_is_loaded_from_the_folder_when_model_path_is_set(monkeypatch):
    seen = []
    monkeypatch.setattr(model_module, "MODEL_PATH", "/app/model")
    monkeypatch.setattr(model_module, "mlflow", fake_mlflow(seen))
    model_module.load_model()
    assert seen == ["/app/model"]


def test_model_is_loaded_by_alias_when_model_path_is_not_set(monkeypatch):
    seen = []
    monkeypatch.setattr(model_module, "MODEL_PATH", None)
    monkeypatch.setattr(model_module, "mlflow", fake_mlflow(seen))
    model_module.load_model()
    assert seen == ["models:/taxi-trip-duration-rf@production"]
