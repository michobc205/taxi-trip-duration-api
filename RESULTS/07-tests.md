# Automatic tests

Question: do the cleaning rules and the API keep their promises, and can this be
checked in seconds, without the taxi data and without a server?

## Setup

The tests are in `tests/` and run with `uv run pytest`. The settings are in
`pyproject.toml`, in the section `[tool.pytest.ini_options]`. The cleaning tests
write tiny made-up files. The API tests use a fake model instead of the
registered model, so no MLflow server and no data file are needed.

## What is tested

| File | Tests | What it checks |
|---|---|---|
| `tests/test_prepare_data.py` | 16 | The four cleaning rules, all rules together, the duration in minutes and the month setting. |
| `tests/test_api.py` | 18 | The API contract: the answers, the input of the model and the refused requests. |
| `tests/test_model.py` | 2 | That `predict_duration` rounds to two decimals and returns a plain float. |
| `tests/conftest.py` | none | The fake model that the other tests share. |

Cleaning rules, 13 single cases. Kept: a normal ride, exactly 1 minute, exactly
60 minutes, 49 mph, the first minute of January and the last minute of January.
Removed: under 1 minute, over 60 minutes, a drop-off before the pickup, distance
0, 54 mph, a pickup in December and a pickup in February.

API: the alive route answers; a valid ride gets the prediction of the fake model;
the model gets one row with the three columns and the types int64, int64 and
float64; a distance of exactly 50 miles is accepted; 8 bad values are refused with
HTTP 422 and the right field is named; 4 missing fields are refused; the model is
not called for bad input; a GET request to `/predict` gets HTTP 405.

## Result

Run on 23 November 2026 on the author's laptop (Windows, Git Bash) with
`uv run --locked pytest -q`: 36 passed in 3.96 seconds (16 + 18 + 2).

## Not tested and limits

- The real registered model, the training script and the loading from MLflow. The
  fake model always gives the same answer, so these tests say nothing about how
  good the model is. The quality is in the other files of this folder.
- Starting the API while MLflow is not running, many requests in a row, and the
  response time of one request (see [03-api.md](03-api.md)).
- The study scripts `src/study_*.py` have no tests.
- Docker: the tests were not run in a container.
