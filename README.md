# Data Analytics Portfolio – Rafat Perveen
Three connected projects built on one **synthetic** UAE retail-sales dataset (5,910 clean orders, 20 products, 500 customers, 2024–2025). No real company data is used.

| # | Project | Skills shown |
|---|---|---|
| 1 | [`01_sql_analysis`](01_sql_analysis) – 7 business questions answered in SQL | CTEs, window functions (LAG, ROW_NUMBER, running totals), joins, KPI design |
| 2 | [`02_powerbi_dashboard`](02_powerbi_dashboard) – Sales Performance dashboard | Star schema, DAX, time intelligence, KPI design, storytelling |
| 3 | [`03_etl_pipeline`](03_etl_pipeline) – Incremental ETL with data-quality controls | Python ETL, validation, idempotent loads, logging, audit trail, unit tests |

## Key finding
Orders with discounts above 20% earn a 14.0% margin, against 35.8% with no discount. Recommendation: cap discounts at 10%.

## Run it
```
pip install pandas
python data/generate_data.py                    # creates the raw CSV files
cd 03_etl_pipeline
python -m unittest -v                           # run the tests
python etl_pipeline.py --reset                  # cleans and loads the data
```
Project 1 uses the cleaned database in `data/clean`; see each project's README for details.
