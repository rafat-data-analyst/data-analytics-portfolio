# Data quality report

- Extracted 6,120 raw order rows
- Removed 120 duplicate orders
- Dropped 60 rows with missing customer_id
- Dropped 30 rows with quantity <= 0
- Filled 58 missing discounts with 0
- Regions standardised: ['Abu Dhabi', 'Al Ain', 'Dubai', 'Ras Al Khaimah', 'Sharjah']
- Validation passed. Clean fact rows: 5,910
