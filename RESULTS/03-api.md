# API results

The API runs locally with `uv run uvicorn app.main:app --port 8000`. The model is
loaded once at startup from the MLflow registry (`models:/taxi-trip-duration-rf@production`).
Requests were sent with `curl` from a second terminal.

## 1. The alive route

Request: `GET /`

~~~
{"message":"NYC Taxi Trip Duration Prediction"}  HTTP 200
~~~

## 2. A valid ride

Request: `POST /predict` with `sample-request.json`

~~~
{"ride_id": "ride-101", "PULocationID": 161, "DOLocationID": 236, "trip_distance": 3.5}
~~~

Answer:

~~~
{"ride_id":"ride-101","PULocationID":161,"DOLocationID":236,"trip_distance":3.5,"predicted_duration":20.48}  HTTP 200
~~~

## 3. Refused: empty ride_id and distance 0

~~~
{"detail":[{"type":"string_too_short","loc":["body","ride_id"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}},{"type":"greater_than","loc":["body","trip_distance"],"msg":"Input should be greater than 0","input":0,"ctx":{"gt":0.0}}]}  HTTP 422
~~~

## 4. Refused: distance 60 (over the limit of 50 miles)

~~~
{"detail":[{"type":"less_than_equal","loc":["body","trip_distance"],"msg":"Input should be less than or equal to 50","input":60,"ctx":{"le":50.0}}]}  HTTP 422
~~~

## Not tested

- Many requests in a row, and the response time of one request.
- Missing fields, and wrong types such as text in the distance.
- Starting the API while MLflow is not running.
