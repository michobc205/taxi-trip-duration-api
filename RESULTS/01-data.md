# Data results

Source: NYC Yellow Taxi trip records, January 2025 (one Parquet file).

## The raw file

| Item | Value |
|---|---|
| Rows | 3,475,226 |
| Columns | 20 |
| Earliest pickup | 2024-12-31 20:47:55 |
| Latest pickup | 2025-02-01 00:00:44 |
| Earliest drop-off | 2024-12-18 07:52:40 |
| Latest drop-off | 2025-02-01 23:44:11 |

The file also holds rides outside January, and at least one ride whose drop-off
is before its pickup.

## The target: duration in minutes (drop-off minus pickup)

| Group of raw rides | Rides |
|---|---|
| Duration below 0 | 124 |
| Duration 0 to under 1 minute | 39,987 |
| Duration 1 to 60 minutes | 3,403,248 |
| Duration over 60 minutes | 31,867 |
| Duration over 180 minutes | 1,377 |
| Duration over 1,440 minutes (one day) | 20 |
| Distance exactly 0 | 90,893 |
| Distance over 100 miles | 162 |
| Pickup outside January 2025 | 22 |

| Percentile of the raw duration | Minutes |
|---|---|
| 1% | 0.67 |
| 5% | 3.37 |
| 50% (median) | 11.70 |
| 95% | 36.20 |
| 99% | 58.92 |

## The speed check

After the first three rules, the average speed of a ride (distance divided by
duration) was checked. How many rides each limit would remove:

| Rule on the average speed | Rides it would remove |
|---|---|
| Over 50 mph | 1,265 |
| Over 60 mph | 424 |
| Over 80 mph | 306 |
| Over 100 mph | 253 |
| Over 150 mph | 188 |

These rows show what each limit **would** remove. Only the 50 mph rule is used in the project, so all rides up to 50 mph are kept in the data and in the model. A limit of 25 mph (the city default) was only measured and not used: it would remove about 5.1% of the rides.

Speed percentiles of these rides: 50% = 9.6 mph, 99% = 35.4 mph,
99.9% = 45.9 mph, 99.99% = 71.4 mph.

After the first three rules, the longest ride was 276,423.57 miles. 152 rides
were over 50 miles.

## The final cleaning rules and what is left

1. Pickup inside January 2025.
2. Duration from 1 to 60 minutes.
3. Distance greater than 0.
4. Average speed at most 50 mph.

| Step | Rides |
|---|---|
| Raw | 3,475,226 |
| After rules 1 to 3 | 3,339,205 (96.09%) |
| After all four rules | 3,337,940 (96.05%) |

After all four rules: median duration 11.67 minutes, longest distance
49.58 miles, highest speed 50.0 mph.

## The split (random, 80/20, seed 42)

| Set | Rides |
|---|---|
| Train | 2,670,352 |
| Validation | 667,588 |
