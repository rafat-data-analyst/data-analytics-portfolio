-- name: 1. Monthly revenue and month-over-month growth
WITH m AS (SELECT strftime('%Y-%m', order_date) AS month, ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit FROM fact_sales GROUP BY 1)
SELECT month, revenue, profit, ROUND(100.0*(revenue - LAG(revenue) OVER (ORDER BY month))/LAG(revenue) OVER (ORDER BY month),1) AS mom_growth_pct FROM m;

-- name: 2. Top 3 products per category (window function)
SELECT * FROM (SELECT p.category, p.product_name, ROUND(SUM(f.revenue),2) AS revenue, ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(f.revenue) DESC) AS rnk FROM fact_sales f JOIN dim_products p USING(product_id) GROUP BY p.category, p.product_name) WHERE rnk<=3 ORDER BY category, rnk;

-- name: 3. Revenue share and margin by region
SELECT region, ROUND(SUM(revenue),2) AS revenue, ROUND(100.0*SUM(revenue)/(SELECT SUM(revenue) FROM fact_sales),1) AS share_pct, ROUND(100.0*SUM(profit)/SUM(revenue),1) AS margin_pct FROM fact_sales GROUP BY region ORDER BY revenue DESC;

-- name: 4. Does discounting hurt margin?
SELECT CASE WHEN discount=0 THEN '0%' WHEN discount<=0.10 THEN '1-10%' WHEN discount<=0.20 THEN '11-20%' ELSE '>20%' END AS discount_band, COUNT(*) AS orders, ROUND(AVG(quantity),2) AS avg_qty, ROUND(100.0*SUM(profit)/SUM(revenue),1) AS margin_pct FROM fact_sales GROUP BY 1 ORDER BY MIN(discount);

-- name: 5. Customer segment value
SELECT c.segment, COUNT(DISTINCT f.customer_id) AS customers, COUNT(*) AS orders, ROUND(SUM(f.revenue)/COUNT(DISTINCT f.customer_id),2) AS revenue_per_customer FROM fact_sales f JOIN dim_customers c USING(customer_id) GROUP BY c.segment ORDER BY revenue_per_customer DESC;

-- name: 6. Repeat-purchase behaviour
WITH o AS (SELECT customer_id, COUNT(*) AS n FROM fact_sales GROUP BY customer_id) SELECT CASE WHEN n=1 THEN 'One-time' WHEN n<=5 THEN '2-5 orders' ELSE '6+ orders' END AS bucket, COUNT(*) AS customers FROM o GROUP BY 1 ORDER BY MIN(n);

-- name: 7. Top 10 customers and cumulative revenue share
WITH c AS (SELECT customer_id, SUM(revenue) AS rev FROM fact_sales GROUP BY 1) SELECT customer_id, ROUND(rev,2) AS revenue, ROUND(100.0*SUM(rev) OVER (ORDER BY rev DESC)/(SELECT SUM(rev) FROM c),1) AS cumulative_share_pct FROM c ORDER BY rev DESC LIMIT 10;
