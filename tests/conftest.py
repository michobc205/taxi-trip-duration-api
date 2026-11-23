"""Shared helpers for the tests."""
import pytest


class FakeModel:
    """A stand-in for the registered model, so no MLflow server is needed."""

    def __init__(self, answer=12.3):
        self.answer = answer
        self.last_input = None

    def predict(self, data):
        self.last_input = data
        return [self.answer]


@pytest.fixture
def fake_model():
    return FakeModel()
