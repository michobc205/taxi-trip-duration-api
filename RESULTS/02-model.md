# Model results

Model: random forest regressor with 50 trees. Inputs: the pickup zone, the
drop-off zone and the trip distance. Target: the duration in minutes.

## The registered baseline model

Trained on a random sample of 200,000 training rides, with a leaf limit of 20
(`min_samples_leaf=20`). Measured on the 667,588 validation rides.

| Metric | Value |
|---|---|
| RMSE | 4.7342 minutes |
| MAE | 3.2442 minutes |
| Naive RMSE (always answers the mean duration) | 9.7832 minutes |

| Item | Value |
|---|---|
| MLflow experiment | taxi-trip-duration |
| Run id | 867f8309380846948890d17140465129 |
| Registered model | taxi-trip-duration-rf, version 1, alias production |

The forest's typical error is about half of the naive error. The median ride
lasts 11.67 minutes, so an error of about 5 minutes is large. The model does not
see the time of day or the weekday.

## Experiment 1: leaf limit

All rows: the 200,000-ride sample, 50 trees, same split.

| Leaf limit | Train time | RMSE | Model size |
|---|---|---|---|
| default (no limit) | 7.8 s | 5.04 | 655.3 MB |
| 5 | 5.5 s | 4.75 | 134.2 MB |
| 20 | 5.7 s | 4.73 | 33.7 MB |
| 50 | 5.1 s | 4.78 | 13.5 MB |
| 100 | 4.3 s | 4.83 | 6.8 MB |

The leaf limit made the model smaller and, up to 20, also better.

## Experiment 2: how much training data

Leaf limit 5, 50 trees.

| Training rides | Train time | RMSE | Model size |
|---|---|---|---|
| 200,000 (sample) | 5.5 s | 4.75 | 134.2 MB |
| 2,670,352 (all) | 175.5 s | 4.55 | 1,222.2 MB |

All rides gave 0.20 minutes lower RMSE, with 32 times the training time and a
model about 9 times bigger. The sample was chosen for the baseline.

## Notes and limits

- The leaf limit of 20 was chosen by looking at the validation RMSE. So the
  reported RMSE is slightly optimistic. A separate test set that is used only
  once would fix this.
- The prediction speed (first timing test, 200,000-ride sample, default
  settings, 667,588 rides): 5.5 seconds.
- All numbers come from one random split with seed 42. They were not repeated
  with other seeds.
