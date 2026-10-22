# Data Analytics Portfolio – Rafat Perveen
Three connected projects built on one **synthetic** UAE retail-sales dataset (5,910 clean orders, 20 products, 500 customers, 2024–2025). No real company data is used.

| # | Project | Skills shown |
|---|---|---|
| 1 | `01_sql_analysis` – 7 business questions answered in SQL | CTEs, window functions (LAG, ROW_NUMBER, running totals), joins, KPI design |
| 2 | `02_powerbi_dashboard` – Sales Performance dashboard | Data modelling, star schema, DAX, KPI design, storytelling |
| 3 | `03_azure_pipeline` – Raw → clean ETL + Azure Blob/ADF load | Python ETL, data quality & validation, Azure Storage, Data Factory |

## Run it
```
pip install pandas
python data/generate_data.py          # creates dirty raw CSVs
python 03_azure_pipeline/etl_pipeline.py   # cleans + loads (data/clean)
python 01_sql_analysis/run_queries.py      # runs all SQL, writes results.md
```
