# Results

All numbers of this project live in this folder. The main README explains the
decisions and has no numbers. The values in files 01 to 03 were measured on
18 November 2026 and the values in files 04 and 05 on 23 November 2026, always
on the author's laptop (Windows, Git Bash), with the random seed 42.

| File | What it holds |
|---|---|
| [01-data.md](01-data.md) | The raw data, the problems we found, and how many rides each cleaning rule removes. |
| [02-model.md](02-model.md) | The model results (RMSE, MAE) and the experiments on leaf limit and data size. |
| [03-api.md](03-api.md) | The real requests to the API and its answers, including the refused ones. |
| [04-february-test.md](04-february-test.md) | The baseline model tested on February, a month it has never seen. |
| [05-time-features.md](05-time-features.md) | Four models with and without the pickup hour and weekday, tested on January and February. |

## Environment

| Item | Value |
|---|---|
| Python | 3.13.17 |
| uv | 0.13.5 |
| Packages installed by `uv sync` | 141 |
| mlflow | 3.17.2 |
| scikit-learn | 1.9.1 |
| pandas | 3.1.0 |
| numpy | 2.5.4 |
| fastapi | 0.162.0 |
| uvicorn | 0.54.0 |
| pydantic | 2.14.1 |
| skops | 0.16.0 |
