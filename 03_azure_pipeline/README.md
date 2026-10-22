# Project 3 – ETL Pipeline with Azure Storage and Data Factory
## What's already built and tested locally
`etl_pipeline.py` extracts raw CSVs, removes 120 duplicates, drops 60 rows missing customer_id and 30 with invalid quantity, fills 58 missing discounts, standardises region names, calculates revenue and profit, validates the result, loads CSV + SQLite, and writes `data/clean/dq_report.md`.

## Azure steps (free account; mostly free-tier, check pricing/credits first)
The Azure steps below are not tested by me; follow them yourself.
1. Create an Azure free account and a **Resource Group** (e.g. `rg-portfolio`).
2. Create a **Storage account** (Standard, LRS). Copy the connection string from *Access keys*.
3. `pip install azure-storage-blob`, set `AZURE_STORAGE_CONNECTION_STRING`, run `python azure_upload.py`. Cleaned CSVs land in container `clean`.
4. Create an **Azure SQL Database** (use the free offer if available, otherwise the lowest serverless tier with auto-pause).
5. Create **Azure Data Factory**: Linked services for Blob Storage and SQL; datasets for each CSV; a **Copy activity** per table (Blob → SQL table); a pipeline with a **daily Schedule trigger**.
6. Connect **Power BI** to Azure SQL (Import mode) to close the loop with Project 2.
7. **Delete the resource group when finished** to avoid charges.

## Architecture
`Raw CSV → Python ETL (clean + validate) → Blob Storage → Data Factory → Azure SQL → Power BI`
Add a screenshot of your ADF pipeline run and a diagram to your GitHub README.
