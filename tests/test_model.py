"""Tests for predict_duration in app/model.py, with a fake model."""
from app.model import predict_duration
from app.schemas import TaxiRide

RIDE = TaxiRide(ride_id="ride-101", PULocationID=161, DOLocationID=236, trip_distance=3.5)


def test_answer_is_rounded_to_two_decimals(fake_model):
    fake_model.answer = 20.4849
    assert predict_duration(fake_model, RIDE) == 20.48


def test_answer_is_a_plain_float(fake_model):
    assert isinstance(predict_duration(fake_model, RIDE), float)
