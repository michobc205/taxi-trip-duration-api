# Docker

Question: can the API run in a container without an MLflow server?

## The problem and the choice

MLflow keeps the files of the registered model at a path on the author's disk
(`file:C:/Users/.../mlartifacts/...`). A container cannot read that path, even if
it can reach the MLflow server. So the container could not load the model by its
alias.

The choice: `src/export_model.py` copies the model that carries the alias
`production` into the folder `model/`. The Dockerfile copies this folder into the
image, and the setting `MODEL_PATH=/app/model` tells `app/model.py` to load the
model from there. Without `MODEL_PATH` the API works as before and loads the
model from the MLflow registry.

## The build

Built on 23 November 2026 on the author's laptop (Windows, Docker Desktop,
Docker 29.9.3) with `docker build -t taxi-trip-duration-api .`.

| Item | Value |
|---|---|
| Base image | python:3.13-slim |
| Python in the image | 3.13.18 |
| Packages installed with `uv sync --locked --no-dev` | 107 |
| Time of the install step | 817.5 seconds (13 min 35 s of it for the downloads) |
| Image size reported by Docker | 2.22 GB on disk (485 MB of content) |

## The run

The container was started with
`docker run --rm -d --name taxi-api -p 8000:8000 taxi-trip-duration-api`.
The MLflow server was stopped, and ports 5000 and 8000 were free before the
start.

| Request | Answer | HTTP |
|---|---|---|
| `GET /` | `{"message":"NYC Taxi Trip Duration Prediction"}` | 200 |
| `POST /predict` with `sample-request.json` | `"predicted_duration":20.48` (the same as in [03-api.md](03-api.md)) | 200 |
| `POST /predict` with a distance of 60 miles | `Input should be less than or equal to 50` | 422 |

The container log shows `Application startup complete` and the three requests.

## Notes and limits

- The container uses the copy of the model from the moment of the export. The
  alias is read at the export, not when the container starts. For a new model
  version the model has to be exported again and the image built again.
- The container runs as the user root. The image is large, because the lock file
  also holds the MLflow server, Optuna and Great Expectations.
- Not tested: the memory and the CPU use, many requests in a row, the response
  time, another computer or another operating system, Docker Compose, and a
  build from a fresh clone. The image was built in the project folder, with a
  model exported from the author's own MLflow database.
- The automatic tests were not run inside the container.
