-- ============================================
-- Task 3.3: OLAP Analytics Queries
-- ============================================

-- Query 1: Monthly Sales Drill-Down Analysis (5 marks)
-- Business Scenario: "The CEO wants to see sales performance broken down by time periods. 
-- Start with yearly total, then quarterly, then monthly sales for 2024."
-- Demonstrates: Drill-down from Year to Quarter to Month

SELECT
    dd.year,
    dd.quarter,
    dd.month_name,
    SUM(fs.total_amount) AS total_sales,
    SUM(fs.quantity_sold) AS total_quantity
FROM
    fact_sales fs
    INNER JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE
    dd.year = 2024
GROUP BY
    dd.year,
    dd.quarter,
    dd.month,
    dd.month_name
ORDER BY
    dd.year ASC,
    dd.quarter ASC,
    dd.month ASC;

-- Query 2: Top 10 Products by Revenue (5 marks)
-- Business Scenario: "The product manager needs to identify top-performing products. 
-- Show the top 10 products by revenue, along with their category, total units sold, 
-- and revenue contribution percentage."
-- Includes: Revenue percentage calculation

SELECT
    dp.product_name,
    dp.category,
    SUM(fs.quantity_sold) AS units_sold,
    SUM(fs.total_amount) AS revenue,
    ROUND(
        (SUM(fs.total_amount) / (SELECT SUM(total_amount) FROM fact_sales)) * 100,
        2
    ) AS revenue_percentage
FROM
    fact_sales fs
    INNER JOIN dim_product dp ON fs.product_key = dp.product_key
GROUP BY
    dp.product_key,
    dp.product_name,
    dp.category
ORDER BY
    revenue DESC
LIMIT 10;

-- Query 3: Customer Segmentation Analysis (5 marks)
-- Business Scenario: "Marketing wants to target high-value customers. Segment customers 
-- into 'High Value' (>₹50,000 spent), 'Medium Value' (₹20,000-₹50,000), and 'Low Value' (<₹20,000). 
-- Show count of customers and total revenue in each segment."
-- Segments: High/Medium/Low value customers

WITH customer_spending AS (
    SELECT
        fs.customer_key,
        SUM(fs.total_amount) AS total_spending
    FROM
        fact_sales fs
    GROUP BY
        fs.customer_key
),
customer_segments AS (
    SELECT
        cs.customer_key,
        cs.total_spending,
        CASE
            WHEN cs.total_spending > 50000 THEN 'High Value'
            WHEN cs.total_spending >= 20000 AND cs.total_spending <= 50000 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS customer_segment
    FROM
        customer_spending cs
)
SELECT
    cs.customer_segment,
    COUNT(DISTINCT cs.customer_key) AS customer_count,
    SUM(cs.total_spending) AS total_revenue,
    ROUND(AVG(cs.total_spending), 2) AS avg_revenue_per_customer
FROM
    customer_segments cs
GROUP BY
    cs.customer_segment
ORDER BY
    CASE cs.customer_segment
        WHEN 'High Value' THEN 1
        WHEN 'Medium Value' THEN 2
        WHEN 'Low Value' THEN 3
    END;

