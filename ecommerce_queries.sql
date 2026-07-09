-- ApexPlanet Data Analytics Internship — Task 2: SQL for Data Extraction
-- Database: ecommerce.db | Table: sales

-- ================= Day 7-8: SQL Fundamentals =================

-- fundamentals_select
SELECT Order_ID, Category, Net_Sales FROM sales LIMIT 5;

-- fundamentals_where
SELECT * FROM sales WHERE Region = 'South' AND Net_Sales > 5000 LIMIT 5;

-- fundamentals_groupby
SELECT Category, ROUND(SUM(Net_Sales), 2) AS total_sales
FROM sales
GROUP BY Category
ORDER BY total_sales DESC;

-- fundamentals_having
SELECT Customer_ID, COUNT(*) AS order_count, ROUND(SUM(Net_Sales),2) AS total_spend
FROM sales
GROUP BY Customer_ID
HAVING order_count > 8
ORDER BY total_spend DESC
LIMIT 10;

-- fundamentals_join_selfdesc
-- (Single fact table here, so JOIN is demonstrated against a derived category-summary subquery)
SELECT s.Order_ID, s.Category, s.Net_Sales, c.avg_category_sales
FROM sales s
JOIN (
    SELECT Category, AVG(Net_Sales) AS avg_category_sales
    FROM sales
    GROUP BY Category
) c ON s.Category = c.Category
LIMIT 5;


-- ================= Day 9-10: Advanced SQL (CTEs, Window Functions, Views) =================

-- cte_top_customers
WITH customer_totals AS (
    SELECT Customer_ID, SUM(Net_Sales) AS total_spend, COUNT(*) AS orders
    FROM sales
    GROUP BY Customer_ID
)
SELECT * FROM customer_totals
ORDER BY total_spend DESC
LIMIT 10;

-- window_rank_products
SELECT Category, Product_Name, total_sales, rank_in_category
FROM (
    SELECT Category, Product_Name, total_sales,
           RANK() OVER (PARTITION BY Category ORDER BY total_sales DESC) AS rank_in_category
    FROM (
        SELECT Category, Product_Name, SUM(Net_Sales) AS total_sales
        FROM sales
        GROUP BY Category, Product_Name
    )
)
WHERE rank_in_category <= 2
ORDER BY Category, rank_in_category;

-- window_lag_monthly
SELECT Order_Month, monthly_sales,
       LAG(monthly_sales) OVER (ORDER BY Order_Month) AS prev_month_sales,
       ROUND(monthly_sales - LAG(monthly_sales) OVER (ORDER BY Order_Month), 2) AS mom_change
FROM (
    SELECT Order_Month, ROUND(SUM(Net_Sales),2) AS monthly_sales
    FROM sales
    GROUP BY Order_Month
)
ORDER BY Order_Month;

-- view_category_performance
SELECT * FROM v_category_performance ORDER BY total_sales DESC;


CREATE VIEW IF NOT EXISTS v_category_performance AS
SELECT Category,
       COUNT(*) AS total_orders,
       ROUND(SUM(Net_Sales), 2) AS total_sales,
       ROUND(AVG(Net_Sales), 2) AS avg_order_value,
       ROUND(SUM(Profit), 2) AS total_profit
FROM sales
GROUP BY Category;


-- ================= 10 Business Questions =================

-- Q1 top5 products by sales
SELECT Product_Name, ROUND(SUM(Net_Sales),2) AS total_sales
FROM sales GROUP BY Product_Name
ORDER BY total_sales DESC LIMIT 5;

-- Q2 monthly sales trend
SELECT Order_Month, ROUND(SUM(Net_Sales),2) AS total_sales
FROM sales GROUP BY Order_Month ORDER BY Order_Month;

-- Q3 customer segmentation by spend
SELECT Customer_Segment, COUNT(DISTINCT Customer_ID) AS customers,
       ROUND(SUM(Net_Sales),2) AS total_sales,
       ROUND(AVG(Net_Sales),2) AS avg_order_value
FROM sales GROUP BY Customer_Segment ORDER BY total_sales DESC;

-- Q4 top region by profit
SELECT Region, ROUND(SUM(Profit),2) AS total_profit
FROM sales GROUP BY Region ORDER BY total_profit DESC;

-- Q5 payment method popularity
SELECT Payment_Method, COUNT(*) AS order_count,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM sales),1) AS pct_of_orders
FROM sales GROUP BY Payment_Method ORDER BY order_count DESC;

-- Q6 avg discount by category
SELECT Category, ROUND(AVG(Discount_Percent),2) AS avg_discount_pct
FROM sales GROUP BY Category ORDER BY avg_discount_pct DESC;

-- Q7 repeat vs onetime customers
SELECT CASE WHEN order_count = 1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
       COUNT(*) AS customers, ROUND(SUM(total_spend),2) AS total_spend
FROM (
    SELECT Customer_ID, COUNT(*) AS order_count, SUM(Net_Sales) AS total_spend
    FROM sales GROUP BY Customer_ID
)
GROUP BY customer_type;

-- Q8 best weekday for sales
SELECT Order_Weekday, ROUND(SUM(Net_Sales),2) AS total_sales, COUNT(*) AS orders
FROM sales GROUP BY Order_Weekday ORDER BY total_sales DESC;

-- Q9 shipmode distribution by region
SELECT Region, Ship_Mode, COUNT(*) AS orders
FROM sales GROUP BY Region, Ship_Mode ORDER BY Region, orders DESC;

-- Q10 high value orders above avg
SELECT Order_ID, Customer_ID, Category, Net_Sales
FROM sales
WHERE Net_Sales > (SELECT AVG(Net_Sales) FROM sales)
ORDER BY Net_Sales DESC
LIMIT 10;
