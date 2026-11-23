# Taxi Trip Duration API

Predicts how many minutes a New York City yellow taxi ride will take. The model
is a random forest. It learns from the January 2025 trip records. Runs are
tracked in MLflow, and the registered model is served by a FastAPI service with
a `/predict` endpoint.

**Results:** see the [RESULTS](RESULTS/) folder. This README has no result
numbers. It explains the work and every decision.

## Why this project is also a study

The task is small. I use it to learn, so at every step I write down the other
options, what I chose, and why. The decisions are in a table further down.
Experiments that are not done yet are listed at the end as follow-up ideas.

## What is in this repository

| Path | What it is |
|---|---|
| `src/prepare_data.py` | Loads the raw file and applies the four cleaning rules. |
| `src/train.py` | Trains the random forest, logs it to MLflow, registers it and sets the alias. |
| `src/study_february.py` | Tests the January model on February, a month it has never seen. |
| `src/study_time_features.py` | Tests whether the pickup hour and weekday help the model. |
| `src/study_speed_limit.py` | Tests training only on rides up to a lower average speed. |
| `src/export_model.py` | Exports the registered model to the folder `model/` for the Docker image. |
| `app/main.py` | The FastAPI service with its two routes. |
| `app/schemas.py` | The input and output rules of the API. |
| `app/model.py` | Loads the model from the registry and predicts for one ride. |
| `tests/` | Automatic tests for the cleaning rules and the API. They use a fake model, so they need no MLflow server or data file. |
| `Dockerfile` | Builds the image that runs the API in a container. |
| `sample-request.json` | An example request for the API. |
| `RESULTS/` | All measured numbers. |
| `data/` | The raw data. It is not in git, and you download it. |

Generated files are not in git: `data/`, `mlflow.db`, `mlartifacts/` and `model/` (see
`.gitignore`).

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/). uv installs the packages.
- About 60 MB of disk space for the data file.
- Docker, only for the part "Run it in Docker". The image needs several GB of disk space.

## Run it, step by step

All commands run in the project folder. They were run on Windows with Git Bash.
You need three terminals, because the MLflow server and the API keep running.

**1. Install the packages**

~~~bash
uv sync
~~~

**2. Download the data** (one Parquet file, January 2025)

~~~bash
mkdir -p data
curl -L -o data/yellow_tripdata_2025-01.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet
~~~

**3. Start the MLflow server** (terminal 1, keep it open)

~~~bash
uv run mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts --allowed-hosts "localhost:5000,127.0.0.1:5000,host.docker.internal:5000"
~~~

**4. Train and register the model** (terminal 2)

~~~bash
uv run python -m src.train
~~~

This logs the run to MLflow, registers the model as `taxi-trip-duration-rf` and
puts the alias `production` on the new version.

**5. Start the API** (terminal 3, keep it open)

~~~bash
uv run uvicorn app.main:app --port 8000
~~~

MLflow must already be running, because the API loads the model once when it
starts.

**6. Send a request** (terminal 2)

~~~bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d @sample-request.json
~~~

The answer holds the ride data and `predicted_duration` in minutes. A request
that breaks the input rules gets HTTP 422 and a message that says which rule.

## Run the tests

The tests need no data file and no MLflow server. They use tiny made-up files and
a fake model. The test settings are in `pyproject.toml`.

~~~bash
uv run pytest
~~~

The result of a run is in [RESULTS](RESULTS/).

## Run it in Docker

The container holds the API and an exported copy of the model, so it needs no
MLflow server. Docker must be running. Steps 1 to 4 of "Run it, step by step"
come first, because the export needs the registered model. Stop the API from
step 5 before you start the container, because both use port 8000.

**1. Export the model** (the MLflow server from step 3 must be running)

~~~bash
uv run python -m src.export_model
~~~

This copies the model that carries the alias `production` into the folder
`model/`.

**2. Build the image** (the first build downloads all packages and takes a while)

~~~bash
docker build -t taxi-trip-duration-api .
~~~

**3. Start the container**

~~~bash
docker run --rm -d --name taxi-api -p 8000:8000 taxi-trip-duration-api
~~~

**4. Send a request** (the same request as in step 6 above)

~~~bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d @sample-request.json
~~~

**5. Stop the container**

~~~bash
docker stop taxi-api
~~~

The MLflow server does not need to run for steps 3 to 5. The container uses the
model as it was when you exported it. For a new model version, export again and
build again. The result of a test run is in [RESULTS](RESULTS/).

## Decisions

Each row names the options I looked at, what I chose, and why. Numbers that
back a decision are in [RESULTS](RESULTS/).

| Decision | Options | Choice | Reason |
|---|---|---|---|
| Getting the data | download with curl, read the web address in Python, download in the browser | curl, once, into `data/` | Every run uses the same file, works offline, and the README can show the command. |
| Cleaning the duration | fixed range of 1 to 60 minutes, cut at percentiles, keep everything | 1 to 60 minutes | Simple to explain and keeps almost all rides. Percentile limits move with every new month. Keeping everything is a follow-up study. |
| Other cleaning rules | none, or distance above 0 and pickup in January | distance above 0, pickup inside January 2025 | A ride with no distance carries no signal for this model. The task is about January. |
| Speed rule | none, a fixed distance cap, a limit on the average speed of 25, 50 or 80 mph | average speed at most 50 mph | The city default limit is 25 mph, so a much higher average over a whole ride is not believable. 25 mph would remove normal rides, for example highway and airport trips, because it is an average. |
| Stricter speed limits for training | limits of 25, 30, 35 or 40 mph instead of 50 | keep 50 mph | Five models were trained with limits from 25 to 50 mph and tested on the same rides. The stricter limits were a little better on slow rides and much worse on fast rides, and 50 mph was best overall (see [RESULTS](RESULTS/)). Limits above 50 mph were not tried. |
| Train and validation split | random 80/20, split by time | random 80/20, seed 42 | Simple and standard. A split by time is closer to real use, so I also tried one with February (next row). |
| Testing on a new month | none, February as a test set only, train on January and February | February as a test set only | The registered model stays the same, so this checks it on rides it has not seen. Training on both months would change the model and leave no new data to test on. See [RESULTS](RESULTS/). |
| Metric | RMSE only, RMSE plus MAE plus a naive baseline | RMSE (the task), MAE, and a naive baseline that always answers the mean | The naive baseline shows whether the model learned anything. |
| Inputs of the model | zone IDs as plain numbers, one-hot zones, one route feature | the two zone IDs as numbers and the trip distance | Cheap on millions of rides and the same three inputs as the API. An ID is a label, so this is not a clean choice. |
| Time inputs | none, hour only, weekday only, hour and weekday, other ways to encode time | hour and weekday as plain numbers, tested as a study only | The baseline does not know the time of day, and the study shows that the hour and the weekday help (see [RESULTS](RESULTS/)). The registered model and the API do not use them yet, because that needs a new input field and a new model version. Other ways to encode the time were not tried. |
| Model settings | default forest, a leaf limit, more data | 50 trees, leaf limit 20, a training sample of 200,000 rides | The default forest was far too large to store and load. The leaf limit made it smaller and also better in the test. All rides gave a small gain for a very large model. |
| Where MLflow keeps data | folder `./mlruns`, SQLite file plus a local server | SQLite file plus a local server | It supports the model registry and aliases. |
| Which model the API uses | a fixed version, an alias | the alias `production` | Moving the alias changes the model without changing the API code. |
| Saving the model | trust nothing, trust one reviewed type | trust `sklearn.tree._tree.Tree` only | MLflow saves scikit-learn models in a safe format that refuses unknown types, and a random forest holds trees of this type. I trained the model myself. |
| Types of the inputs | let pandas choose, force int64 and float64 | force int64 and float64 | The API receives plain JSON numbers, so the model signature must match. |
| API routes | one route, a single and a batch route | `GET /` and `POST /predict` | The task asks for `/predict`. A batch route is a follow-up. |
| API input rules | none, or checks on every field | id not empty, both zones above 0, distance above 0 and at most 50 miles | The model never saw a longer ride. Bad input is refused with HTTP 422 before the model is called. |
| Automatic tests | none, tests with the real model and an MLflow server, tests with a fake model | tests with a fake model | They run in a few seconds and need no server and no data file. They check the cleaning rules and the API contract, but not the quality of the real model. That is in [RESULTS](RESULTS/). |
| When the API loads the model | once at startup, on every request | once at startup | Faster. The price is a restart when the model changes, and MLflow must be running at start. |
| Docker and the model files | the container reads the model from the MLflow server, a copy of the model inside the image | a copy of the model inside the image, made by `src/export_model.py` | MLflow keeps the model files at a path on my disk, which a container cannot read, so it could not load the model even with the server reachable. The image needs no server. The price is an export and a new build whenever the model changes. |
| Docker base image and packages | python image with pip, python image with uv and `uv.lock` | `python:3.13-slim` with uv and `uv.lock` | The image gets exactly the package versions that are pinned in `uv.lock`. The image is large, see [RESULTS](RESULTS/), because the lock file also holds the MLflow server and the tuning tools. |

## Limits

- The registered model sees only the two zones and the distance. It does not know
  the time of day or the weekday. A study with the hour and the weekday gave a
  lower error (see RESULTS), but the registered model and the API do not use them yet.
- It was trained on rides of 1 to 60 minutes. Its answers for longer rides are
  not reliable.
- One month of data for training and one random split. The model was also tested
  once on February, but nothing was repeated with other seeds.
- The leaf limit was chosen on the validation set, so the reported error is
  slightly optimistic. The February test gave a similar error, so the effect looks
  small. A separate test set that is used only once would still be cleaner.
- Without Docker, the API needs MLflow running when it starts, and it needs a
  restart to use a new model version.
- The tests use a fake model. They do not test the real registered model, the
  training script or the loading from MLflow. The tests are not run in the
  container.
- The model in the Docker image is the copy from the moment of the export. The
  container runs as root, and the image is large.

## Follow-up ideas

These are not done yet. Each one is a possible next study.

- A simple linear model as a second baseline, and a second model family.
- Cleaning studies: percentile limits, no duration limit, and speed limits above
  50 mph (limits of 25 to 40 mph were tried, see RESULTS).
- A separate test set that is used only once, and a split by time with more months
  (February is done, see RESULTS).
- More inputs: one-hot zones, a route feature, and other ways to encode the hour
  (hour and weekday as plain numbers are done, see RESULTS).
- Tuning with grid search or Optuna, and training on all rides with a larger leaf limit.
- More tests: the training script, the real model and the loading from MLflow
  (tests for the cleaning rules and the API are done, see RESULTS).
- Docker next steps: a smaller image, a non-root user, and Docker Compose with
  MLflow (the container with an exported model is done, see RESULTS).
- A batch route, an upper limit for the zone IDs, and zone IDs as float columns.
- Loading the model on every request, and the `./mlruns` way of tracking.

## Data and license

Data: public NYC Taxi and Limousine Commission (TLC) trip record data, yellow
taxi, January 2025, from the
[TLC trip record page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
The data was not created by the TLC, and the TLC makes no promise that it is
accurate. This project is not connected to the TLC. The data files are not part
of this repository. Please check the terms of use on the TLC and nyc.gov pages
before you reuse the data.

The `LICENSE` file is the license of this repository (the code only).
