# Project 3 – Incremental ETL Pipeline with Data Quality Controls

A production-style Python ETL for retail sales orders (synthetic data). It loads only new data, rejects bad rows with a reason, keeps an audit trail and validates the result after every run.

**Raw files → clean + validate → quarantine rejects → incremental load (SQLite) → CSV exports for Power BI → data-quality report**

## What it does
| Feature | How it works |
|---|---|
| **Incremental and idempotent** | Loads only `order_id`s not already in the database. Re-running loads 0 duplicate rows. |
| **Data-quality rules** | Duplicates, missing customer, invalid quantity, unknown product, invalid date and out-of-range discount are rejected. |
| **Quarantine** | Rejected rows go to `data/pipeline_output/rejected/` with a `reject_reason` column. |
| **Fixes, not just rejects** | Region names standardised (`dubai ` → `Dubai`), missing discounts filled with 0. |
| **Audit trail** | Each processed file is recorded in the `etl_runs` table and in `logs/etl.log`. |
| **Database integrity** | Primary key on `order_id`, `NOT NULL` and `CHECK (quantity > 0)` constraints. |
| **Post-load validation** | Checks for duplicate IDs, negative revenue, missing customers and orphan products; the run fails if any check fails. |
| **Automated tests** | 8 unit tests cover each cleaning rule (`python -m unittest -v`). |
| **Scheduling** | `run_pipeline.bat` runs the pipeline for Windows Task Scheduler. |

## Run it
```
pip install pandas
python data/generate_data.py                      # once: create the raw files (from the repo root)
cd 03_etl_pipeline
python -m unittest -v                             # run the tests
python etl_pipeline.py --reset                    # first load
python simulate_new_batch.py                      # a new daily file arrives
python etl_pipeline.py                            # loads only the new rows
python etl_pipeline.py                            # run again: loads nothing (idempotent)
```

## Sample results (from the run history in `sample_output/dq_report.md`)
| Run | File | Rows in | Rejected | Skipped (already loaded) | Loaded |
|---|---|---|---|---|---|
| 1 | orders.csv | 6,120 | 210 | 0 | **5,910** |
| 2 | orders_batch2.csv | 390 | 10 | 30 | **350** |
| 3 (re-run) | both files | – | – | all | **0** |

- First load: 120 duplicates, 60 missing customers and 30 invalid quantities rejected; 58 missing discounts filled. The 5,910 clean orders match Projects 1 and 2.
- Second file: 350 new orders loaded, 30 already-loaded orders skipped, 10 bad rows rejected.
- Re-running adds no duplicates.

## Schedule it (Windows)
1. Open **Task Scheduler**, then **Create Basic Task**.
2. Trigger: **Daily**. Action: **Start a program** and choose `run_pipeline.bat`.
3. Check `logs/scheduler.log` and `logs/etl.log` after each run.

## Possible next step
The same design maps onto cloud services: files in object storage, a scheduled orchestrator and a cloud SQL database. This project runs locally; no cloud deployment is claimed.

## Skills shown
Python · pandas · SQL/SQLite · ETL design · data quality and validation · idempotent loads · logging and audit trails · unit testing · scheduling
