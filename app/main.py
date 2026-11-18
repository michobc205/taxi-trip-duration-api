"""FastAPI service that predicts the duration of a NYC taxi trip."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.model import load_model, predict_duration
from app.schemas import Prediction, TaxiRide


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    yield


app = FastAPI(title="Taxi trip duration API", lifespan=lifespan)


@app.get("/")
def index():
    return {"message": "NYC Taxi Trip Duration Prediction"}


@app.post("/predict", response_model=Prediction)
def predict(ride: TaxiRide):
    duration = predict_duration(app.state.model, ride)
    return Prediction(**ride.model_dump(), predicted_duration=duration)
