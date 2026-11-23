"""Tests for the API contract.

A fake model is used, so no MLflow server is needed to run these tests.
"""
import pytest
from fastapi.testclient import TestClient

import app.main as main

VALID = {"ride_id": "ride-101", "PULocationID": 161, "DOLocationID": 236, "trip_distance": 3.5}


@pytest.fixture
def client(monkeypatch, fake_model):
    monkeypatch.setattr(main, "load_model", lambda: fake_model)
    with TestClient(main.app) as test_client:
        yield test_client


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NYC Taxi Trip Duration Prediction"}


def test_valid_ride_gets_the_prediction(client):
    response = client.post("/predict", json=VALID)
    assert response.status_code == 200
    assert response.json() == {**VALID, "predicted_duration": 12.3}


def test_model_gets_one_row_with_the_right_types(client, fake_model):
    client.post("/predict", json=VALID)
    data = fake_model.last_input
    assert list(data.columns) == ["PULocationID", "DOLocationID", "trip_distance"]
    assert len(data) == 1
    assert [str(t) for t in data.dtypes] == ["int64", "int64", "float64"]
    assert data.iloc[0].tolist() == [161, 236, 3.5]


def test_distance_of_exactly_50_miles_is_accepted(client):
    response = client.post("/predict", json={**VALID, "trip_distance": 50})
    assert response.status_code == 200


@pytest.mark.parametrize(
    "field, value",
    [
        ("ride_id", ""),
        ("PULocationID", 0),
        ("DOLocationID", 0),
        ("PULocationID", "abc"),
        ("trip_distance", 0),
        ("trip_distance", -1),
        ("trip_distance", 60),
        ("trip_distance", "far"),
    ],
)
def test_bad_value_is_refused_and_the_field_is_named(client, field, value):
    response = client.post("/predict", json={**VALID, field: value})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


@pytest.mark.parametrize("field", list(VALID))
def test_missing_field_is_refused(client, field):
    payload = {key: value for key, value in VALID.items() if key != field}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


def test_model_is_not_called_for_bad_input(client, fake_model):
    client.post("/predict", json={**VALID, "trip_distance": 60})
    assert fake_model.last_input is None


def test_predict_needs_post(client):
    assert client.get("/predict").status_code == 405
