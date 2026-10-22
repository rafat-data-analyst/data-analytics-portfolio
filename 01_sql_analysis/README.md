# Project 1 – SQL Sales Analysis
**Data:** `data/clean/sales.db` (SQLite; star schema: `fact_sales`, `dim_products`, `dim_customers`).
**Queries:** `queries.sql` · **Results:** `results.md` (re-create with `python run_queries.py`).

## Business questions
1. How do revenue and profit trend month over month? (LAG)
2. Which 3 products lead each category? (ROW_NUMBER + PARTITION BY)
3. Which regions drive revenue, and at what margin?
4. Does discounting increase volume or just reduce margin?
5. Which customer segment is most valuable?
6. How often do customers repeat-purchase?
7. How concentrated is revenue in the top customers? (cumulative share)

## Key findings (synthetic data)
- Dubai (36.6%) and Abu Dhabi (31.1%) generate about two-thirds of revenue; margins are similar (~29%) across regions.
- **Discounts did not lift quantity** (avg qty ~1.9–2.0 in every band) but cut margin from 35.8% (no discount) to 14.0% (>20%). Recommendation: cap discounts at 10% and test targeted offers.
- Revenue per customer is similar across segments, so growth should come from acquisition and frequency, not one segment.

> Note: data is randomly generated, so patterns are illustrative. In an interview, explain the method and the recommendation logic.
