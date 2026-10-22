# Project 2 – Power BI Sales Performance Dashboard
Power BI files (.pbix) can't be generated outside Power BI Desktop, so this is a build kit. Building it yourself (about 2–3 hours) is what makes it truly yours.

## Step 1 – Load data (Get Data > Text/CSV)
`data/clean/fact_sales.csv`, `dim_products.csv`, `dim_customers.csv`. In Power Query set `order_date` and `signup_date` to Date.

## Step 2 – Model (star schema)
- `dim_products[product_id]` 1 → * `fact_sales[product_id]`
- `dim_customers[customer_id]` 1 → * `fact_sales[customer_id]`
- Create a Date table and relate `Date[Date]` → `fact_sales[order_date]`:
```
Date = ADDCOLUMNS(CALENDAR(DATE(2024,1,1), DATE(2025,12,31)),
  "Year", YEAR([Date]), "MonthNo", MONTH([Date]), "Month", FORMAT([Date],"MMM"), "Quarter", "Q" & QUARTER([Date]))
```
Mark it as the date table.

## Step 3 – DAX measures
```
Revenue = SUM(fact_sales[revenue])
Profit = SUM(fact_sales[profit])
Margin % = DIVIDE([Profit], [Revenue])
Orders = DISTINCTCOUNT(fact_sales[order_id])
Avg Order Value = DIVIDE([Revenue], [Orders])
Revenue LY = CALCULATE([Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
Revenue YoY % = DIVIDE([Revenue] - [Revenue LY], [Revenue LY])
Revenue YTD = TOTALYTD([Revenue], 'Date'[Date])
Avg Discount % = AVERAGE(fact_sales[discount])
Revenue Rank (Product) = RANKX(ALL(dim_products[product_name]), [Revenue])
```

## Step 4 – Page layout
- **Top row:** cards for Revenue, Profit, Margin %, Orders, Avg Order Value, Revenue YoY %.
- **Left:** line chart of Revenue and Revenue LY by Month.
- **Middle:** bar chart of Revenue by Category (drill to Product); map or bar of Revenue by Region.
- **Right:** donut of Revenue by Channel; table of the top 10 products with Margin %.
- **Slicers:** Year, Quarter, Region, Segment.
- **Second page ("Discount Insight"):** column chart of Margin % by discount band (create a calculated column on `fact_sales`) with a short text box recommending a discount cap.
- Use one colour palette, a title, and tooltips with Margin %.

## Step 5 – Publish
Sign in to a free Power BI account, publish, and use File > Export (PDF) or Publish to web. Add screenshots to your GitHub README and LinkedIn Featured section.
