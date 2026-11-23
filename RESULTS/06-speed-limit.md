# Speed limit on the training rides

Question: does the model get better or worse when it learns only from rides up
to a lower average speed? The baseline in [02-model.md](02-model.md) learns from
all cleaned rides up to 50 mph.

## Setup

Five random forests are trained on January only. All use the same settings as
the baseline: a random sample of 200,000 training rides, 50 trees, leaf limit 20,
seed 42, and the same three inputs. They differ only in which training rides are
allowed: rides with an average speed up to 25, 30, 35, 40 or 50 mph. The 50 mph
model is the baseline, because the cleaning rules already stop at 50 mph. The
script is `src/study_speed_limit.py` and runs with
`uv run python -m src.study_speed_limit`. It does not use MLflow, so the
registered model and the API are not changed.

All five models are tested on the same rides, so the numbers can be compared.
If each model were tested on its own rides, a strict limit would look better
only because its test rides are easier.

| Test set | Rides |
|---|---|
| January validation, up to 25 mph | 633,495 |
| January validation, over 25 mph | 34,093 (5.11%) |
| January validation, all | 667,588 |
| February, all (cleaned, up to 50 mph) | 3,426,353 |

## Results

RMSE in minutes. "Rides allowed" is the number of training rides below the
limit, out of 2,670,352 January training rides. Each model then trains on a
random sample of 200,000 of them.

| Limit (mph) | Rides allowed | Slow rides (up to 25 mph) | Fast rides (over 25 mph) | January, all | February, all | February MAE |
|---|---|---|---|---|---|---|
| 25 | 2,534,177 | 4.2951 | 14.1053 | 5.2599 | 5.2598 | 3.5252 |
| 30 | 2,603,644 | 4.3454 | 11.0071 | 4.9097 | 4.9864 | 3.3926 |
| 35 | 2,642,512 | 4.4225 | 9.1274 | 4.7764 | 4.8894 | 3.3399 |
| 40 | 2,660,773 | 4.4741 | 8.2728 | 4.7424 | 4.8696 | 3.3242 |
| 50 (baseline) | 2,670,352 | 4.5081 | 7.8256 | 4.7342 | 4.8692 | 3.3186 |

The 50 mph row is the same as the baseline in [02-model.md](02-model.md) and
[04-february-test.md](04-february-test.md).

Change in RMSE compared with the 50 mph baseline:

| Limit (mph) | Slow rides | Fast rides | January, all | February, all |
|---|---|---|---|---|
| 25 | -0.2130 (-4.7%) | +6.2797 (+80.2%) | +0.5257 (+11.1%) | +0.3906 (+8.0%) |
| 30 | -0.1627 (-3.6%) | +3.1815 (+40.7%) | +0.1755 (+3.7%) | +0.1172 (+2.4%) |
| 35 | -0.0856 (-1.9%) | +1.3018 (+16.6%) | +0.0422 (+0.9%) | +0.0202 (+0.4%) |
| 40 | -0.0340 (-0.8%) | +0.4472 (+5.7%) | +0.0082 (+0.2%) | +0.0004 (+0.01%) |

## What the numbers show

- A stricter limit helps a little on slow rides. With 25 mph the RMSE on slow
  rides is 4.2951 instead of 4.5081.
- It hurts a lot on fast rides, which are 5.1% of the January validation rides.
  With 25 mph the RMSE there is 14.1053 instead of 7.8256.
- Over all rides, the 50 mph baseline has the lowest RMSE on both January
  (4.7342) and February (4.8692). The 40 mph model is almost the same on
  February and slightly worse on January.
- In this test the 50 mph rule held up. Limits of 25 to 40 mph were not better
  overall.

## Notes and limits

- Limits above 50 mph, or no limit at all, were not tried. So 50 mph is not
  shown to be the best limit. It only beat the stricter ones.
- The speed of a ride is its distance divided by its duration. The duration is
  the number the model has to predict, so the speed is not known when a real
  request arrives. The two columns "slow rides" and "fast rides" show what the
  models learned, but they are not a split that could be used in real life. The
  columns "January, all" and "February, all" are the fair comparison.
- One model type, one random seed and one training sample of 200,000 rides per
  model. February was already used in two other studies, so it is not an
  untouched test set.
- All numbers were measured on 23 November 2026 on the author's laptop
  (Windows, Git Bash), with the random seed 42.
