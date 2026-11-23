# Hour and weekday as inputs

Question: does the model get better when it also knows the hour and the weekday
of the pickup? The baseline in [02-model.md](02-model.md) does not know them.

## Setup

Four random forests are trained on January only. All use the same settings as
the baseline: a random sample of 200,000 January training rides, 50 trees, leaf
limit 20, seed 42. They differ only in their inputs. The hour (0 to 23) and the
weekday (0 to 6, Monday is 0) are taken from the pickup time and are used as
plain whole numbers. Each model is tested on the January validation rides and on
all cleaned February rides (see [04-february-test.md](04-february-test.md)). The
script is `src/study_time_features.py` and runs with
`uv run python -m src.study_time_features`. It does not use MLflow, so the
registered model and the API are not changed.

## Results

RMSE and MAE in minutes. The baseline rows are the same as in
[02-model.md](02-model.md) and [04-february-test.md](04-february-test.md).

| Inputs | January RMSE | January MAE | February RMSE | February MAE |
|---|---|---|---|---|
| baseline (zones and distance) | 4.7342 | 3.2442 | 4.8692 | 3.3186 |
| + hour | 4.3865 | 2.9748 | 4.5593 | 3.0757 |
| + weekday | 4.6908 | 3.2065 | 4.8147 | 3.2686 |
| + hour + weekday | 4.2535 | 2.8662 | 4.3985 | 2.9461 |

On February, RMSE compared with the baseline:

| Inputs | Change in RMSE | Share |
|---|---|---|
| + hour | -0.3099 | 6.4% |
| + weekday | -0.0545 | 1.1% |
| + hour + weekday | -0.4707 | 9.7% |

The hour gives most of the gain. The weekday alone gives little, but with the
hour it adds more than it adds alone. On January the changes are similar:
-0.3477 for the hour (7.3%), -0.0434 for the weekday (0.9%) and -0.4807 for both
(10.2%). The February RMSE of the full model is 4.3985 minutes, which is 45% of
the naive RMSE of 9.7132 minutes.

## February, error by part of the day

RMSE in minutes, baseline against the model with hour and weekday.

| Part of the day | Rides | Baseline | Hour + weekday | Change |
|---|---|---|---|---|
| night, 0 to 5 | 296,536 | 4.8626 | 3.6620 | -24.7% |
| morning, 6 to 9 | 423,042 | 5.5275 | 4.9758 | -10.0% |
| midday, 10 to 15 | 1,026,974 | 5.1444 | 4.6457 | -9.7% |
| evening, 16 to 19 | 890,502 | 4.7101 | 4.3863 | -6.9% |
| late, 20 to 23 | 789,299 | 4.2658 | 3.9862 | -6.6% |

The gain is largest at night and smallest in the evening.

## How much the forest uses each input

For the model with all five inputs: trip distance 0.89, pickup hour 0.048,
drop-off zone 0.024, pickup zone 0.021, weekday 0.017. These values show how
much the forest splits on an input. They do not show how much an input helps:
the hour has a small value here and still lowers the error clearly.

## Notes and limits

- One model type, one random seed, one month of training and one test month.
- February was already used in the February test. This is a second look at the
  same month, not a separate test set that was kept untouched.
- The hour and the weekday are plain numbers. Hour 23 and hour 0 are far apart as
  numbers, and the forest has to split twice to treat them as neighbours. Other
  ways to encode the time (one-hot columns, a circle) were not tried.
- Public holidays were not looked at.
- The registered model and the API do not use the hour or the weekday. Using
  them in the API would need a new input field and a new model version.
- All numbers were measured on 23 November 2026 on the author's laptop
  (Windows, Git Bash), with the random seed 42.
