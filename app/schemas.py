"""Input and output rules (the contract) of the prediction API."""
from pydantic import BaseModel, Field

# The model was trained on rides of at most 60 minutes at most 50 mph,
# so it never saw a ride longer than 50 miles. The API refuses such input.
MAX_TRIP_MILES = 50


class TaxiRide(BaseModel):
    ride_id: str = Field(min_length=1)
    PULocationID: int = Field(gt=0)
    DOLocationID: int = Field(gt=0)
    trip_distance: float = Field(gt=0, le=MAX_TRIP_MILES)


class Prediction(TaxiRide):
    predicted_duration: float
