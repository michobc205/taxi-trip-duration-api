# February test (split by time)

Question: does the baseline model still work on a month it has never seen?

## Setup

The model is the same as the baseline in [02-model.md](02-model.md). It is
trained on January only: a random sample of 200,000 January training rides,
50 trees, leaf limit 20, seed 42. It is then tested on two sets. The script is
`src/study_february.py` and runs with `uv run python -m src.study_february`.
It does not use MLflow, so the registered model and the API are not changed.

February goes through the same four cleaning rules as January. Only the month
in rule 1 changes (it is a setting of `load_clean_data`).

| Month | Raw rides | Rides kept | Share kept |
|---|---|---|---|
| January 2025 | 3,475,226 | 3,337,940 | 96.05% |
| February 2025 | 3,577,543 | 3,426,353 | 95.77% |

The raw February file has 31 rides with a pickup outside February. Rule 1
removes them.

## Results

| Set | Rides | RMSE (min) | MAE (min) | Naive RMSE (min) | Median duration (min) |
|---|---|---|---|---|---|
| January validation (random 20% of January) | 667,588 | 4.7342 | 3.2442 | 9.7832 | 11.68 |
| February (never seen) | 3,426,353 | 4.8692 | 3.3186 | 9.7132 | 12.17 |

The January row is the same as in [02-model.md](02-model.md).

On February the RMSE is 0.1350 minutes higher (2.9%) and the MAE is 0.0744
minutes higher (2.3%). In both sets the model's error is about half of the
naive error. The median February ride is 0.49 minutes longer than the median
January validation ride.

## Notes and limits

- One new month, one model and one random seed. A month in summer could look
  different. February is a short winter month.
- The naive answer is the January mean (14.2 minutes), because that is all a
  model trained on January could know.
- This is a split by time, but February was used once for this study. It is not
  a separate test set that was kept untouched for the final model.
- All numbers were measured on 23 November 2026 on the author's laptop
  (Windows, Git Bash), with the random seed 42.
