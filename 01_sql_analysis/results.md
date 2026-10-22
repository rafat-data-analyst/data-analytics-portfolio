# SQL analysis results

## 1. Monthly revenue and month-over-month growth

```sql
WITH m AS (SELECT strftime('%Y-%m', order_date) AS month, ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit FROM fact_sales GROUP BY 1)
SELECT month, revenue, profit, ROUND(100.0*(revenue - LAG(revenue) OVER (ORDER BY month))/LAG(revenue) OVER (ORDER BY month),1) AS mom_growth_pct FROM m;
```

| month | revenue | profit | mom_growth_pct |
|---|---|---|---|
| 2024-01 | 241821.06 | 71147.55 | None |
| 2024-02 | 219303.72 | 64305.82 | -9.3 |
| 2024-03 | 211613.15 | 59260.82 | -3.5 |
| 2024-04 | 195495.16 | 57832.27 | -7.6 |
| 2024-05 | 234351.06 | 70917.3 | 19.9 |
| 2024-06 | 172821.72 | 50810.5 | -26.3 |
| 2024-07 | 240134.06 | 72593.29 | 38.9 |
| 2024-08 | 223175.64 | 66873.81 | -7.1 |
| 2024-09 | 208297.72 | 55903.47 | -6.7 |
| 2024-10 | 248332.54 | 70367.71 | 19.2 |
| 2024-11 | 207910.78 | 58772.03 | -16.3 |
| 2024-12 | 245612.59 | 74346.08 | 18.1 |
| 2025-01 | 244540.06 | 73876.84 | -0.4 |
| 2025-02 | 195281.39 | 55201.19 | -20.1 |
| 2025-03 | 239906.79 | 74558.46 | 22.9 |
| 2025-04 | 200883.36 | 60781.24 | -16.3 |
| 2025-05 | 247781.72 | 72610.39 | 23.3 |
| 2025-06 | 229834.75 | 67784.19 | -7.2 |
| 2025-07 | 271758.14 | 79105.54 | 18.2 |
| 2025-08 | 233715.83 | 64344.77 | -14.0 |
| 2025-09 | 265735.11 | 78505.93 | 13.7 |
| 2025-10 | 204819.5 | 62262.28 | -22.9 |
| 2025-11 | 229134.99 | 66142.61 | 11.9 |
| 2025-12 | 243013.48 | 75831.4 | 6.1 |

## 2. Top 3 products per category (window function)

```sql
SELECT * FROM (SELECT p.category, p.product_name, ROUND(SUM(f.revenue),2) AS revenue, ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(f.revenue) DESC) AS rnk FROM fact_sales f JOIN dim_products p USING(product_id) GROUP BY p.category, p.product_name) WHERE rnk<=3 ORDER BY category, rnk;
```

| category | product_name | revenue | rnk |
|---|---|---|---|
| Electronics | Tablet | 745702.11 | 1 |
| Electronics | Headphones | 675510.55 | 2 |
| Electronics | Laptop | 601515.77 | 3 |
| Fashion | Sunglasses | 369291.72 | 1 |
| Fashion | Watch | 264608.07 | 2 |
| Fashion | Sneakers | 260510.49 | 3 |
| Home | Blender | 258402.58 | 1 |
| Home | Vacuum Cleaner | 204522.82 | 2 |
| Home | Desk Lamp | 83500.24 | 3 |
| Sports | Tennis Racket | 251105.52 | 1 |
| Sports | Yoga Mat | 246384.27 | 2 |
| Sports | Cycling Helmet | 223311.96 | 3 |

## 3. Revenue share and margin by region

```sql
SELECT region, ROUND(SUM(revenue),2) AS revenue, ROUND(100.0*SUM(revenue)/(SELECT SUM(revenue) FROM fact_sales),1) AS share_pct, ROUND(100.0*SUM(profit)/SUM(revenue),1) AS margin_pct FROM fact_sales GROUP BY region ORDER BY revenue DESC;
```

| region | revenue | share_pct | margin_pct |
|---|---|---|---|
| Dubai | 1994588.08 | 36.6 | 29.5 |
| Abu Dhabi | 1697099.39 | 31.1 | 29.6 |
| Sharjah | 822658.38 | 15.1 | 29.8 |
| Al Ain | 522048.87 | 9.6 | 28.6 |
| Ras Al Khaimah | 418879.6 | 7.7 | 28.4 |

## 4. Does discounting hurt margin?

```sql
SELECT CASE WHEN discount=0 THEN '0%' WHEN discount<=0.10 THEN '1-10%' WHEN discount<=0.20 THEN '11-20%' ELSE '>20%' END AS discount_band, COUNT(*) AS orders, ROUND(AVG(quantity),2) AS avg_qty, ROUND(100.0*SUM(profit)/SUM(revenue),1) AS margin_pct FROM fact_sales GROUP BY 1 ORDER BY MIN(discount);
```

| discount_band | orders | avg_qty | margin_pct |
|---|---|---|---|
| 0% | 2317 | 1.93 | 35.8 |
| 1-10% | 1381 | 2.01 | 30.7 |
| 11-20% | 1492 | 1.92 | 22.7 |
| >20% | 720 | 1.97 | 14.0 |

## 5. Customer segment value

```sql
SELECT c.segment, COUNT(DISTINCT f.customer_id) AS customers, COUNT(*) AS orders, ROUND(SUM(f.revenue)/COUNT(DISTINCT f.customer_id),2) AS revenue_per_customer FROM fact_sales f JOIN dim_customers c USING(customer_id) GROUP BY c.segment ORDER BY revenue_per_customer DESC;
```

| segment | customers | orders | revenue_per_customer |
|---|---|---|---|
| Consumer | 270 | 3228 | 11013.66 |
| Small Business | 90 | 1094 | 10803.4 |
| Corporate | 140 | 1588 | 10780.56 |

## 6. Repeat-purchase behaviour

```sql
WITH o AS (SELECT customer_id, COUNT(*) AS n FROM fact_sales GROUP BY customer_id) SELECT CASE WHEN n=1 THEN 'One-time' WHEN n<=5 THEN '2-5 orders' ELSE '6+ orders' END AS bucket, COUNT(*) AS customers FROM o GROUP BY 1 ORDER BY MIN(n);
```

| bucket | customers |
|---|---|
| 2-5 orders | 9 |
| 6+ orders | 491 |

## 7. Top 10 customers and cumulative revenue share

```sql
WITH c AS (SELECT customer_id, SUM(revenue) AS rev FROM fact_sales GROUP BY 1) SELECT customer_id, ROUND(rev,2) AS revenue, ROUND(100.0*SUM(rev) OVER (ORDER BY rev DESC)/(SELECT SUM(rev) FROM c),1) AS cumulative_share_pct FROM c ORDER BY rev DESC LIMIT 10;
```

| customer_id | revenue | cumulative_share_pct |
|---|---|---|
| C0483 | 28472.24 | 0.5 |
| C0017 | 25641.92 | 1.0 |
| C0235 | 23675.93 | 1.4 |
| C0170 | 23480.32 | 1.9 |
| C0255 | 23456.29 | 2.3 |
| C0342 | 23060.11 | 2.7 |
| C0219 | 22954.31 | 3.1 |
| C0461 | 22236.78 | 3.5 |
| C0470 | 21708.96 | 3.9 |
| C0232 | 21645.38 | 4.3 |
