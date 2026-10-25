# Data quality report

Generated: 2026-10-25 15:24

## Current warehouse state
- Orders loaded: **6,260**
- Total revenue: **5,792,205.79**
- Total profit: **1,704,227.54**

## Run history
| Time | File | Rows in | Rejected | Skipped (already loaded) | Loaded | Status |
|---|---|---|---|---|---|---|
| 2026-10-25T15:24:29 | orders.csv | 6120 | 210 | 0 | 5910 | SUCCESS |
| 2026-10-25T15:24:34 | orders.csv | 6120 | 210 | 5910 | 0 | SUCCESS |
| 2026-10-25T15:24:34 | orders_batch2.csv | 390 | 10 | 30 | 350 | SUCCESS |
| 2026-10-25T15:24:34 | orders.csv | 6120 | 210 | 5910 | 0 | SUCCESS |
| 2026-10-25T15:24:34 | orders_batch2.csv | 390 | 10 | 380 | 0 | SUCCESS |

## Rejected rows by reason
- duplicate_in_batch: 120
- invalid_quantity: 35
- missing_customer_id: 65
