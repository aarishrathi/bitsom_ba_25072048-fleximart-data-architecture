-- Query 1: Customer Purchase History
-- Business Question: Generate a detailed report showing each customer's name, email, 
-- total number of orders placed, and total amount spent. Include only customers 
-- who have placed at least 2 orders and spent more than ₹5,000.
-- Order by total amount spent in descending order.
-- Expected to return customers with 2+ orders and >5000 spent
--
-- Logic: Joining orders and order_items creates duplicates if you just COUNT(orders.order_id).
-- Trap: You get the count of items, not orders.
-- Solution: Use COUNT(DISTINCT o.order_id) to get the true order count.
-- Note: Since we must join order_items per prompt, we use SUM(oi.subtotal) for total_spent.
-- If we didn't join order_items, we could use SUM(o.total_amount) instead.

SELECT 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.subtotal) AS total_spent
FROM 
    customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY 
    c.customer_id, c.first_name, c.last_name, c.email
HAVING 
    COUNT(DISTINCT o.order_id) >= 2 
    AND SUM(oi.subtotal) > 5000
ORDER BY 
    total_spent DESC;

-- Query 2: Product Sales Analysis
-- Business Question: For each product category, show the category name, 
-- number of different products sold, total quantity sold, and total revenue generated. 
-- Only include categories that have generated more than ₹10,000 in revenue. 
-- Order by total revenue descending.
-- Expected to return categories with >10000 revenue
--
-- Logic: Simple aggregation. We group by category and sum up the subtotal from order_items.
-- Constraint: HAVING SUM(subtotal) > 10000.

SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) AS num_products,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.subtotal) AS total_revenue
FROM 
    products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY 
    p.category
HAVING 
    SUM(oi.subtotal) > 10000
ORDER BY 
    total_revenue DESC;

-- Query 3: Monthly Sales Trend
-- Business Question: Show monthly sales trends for the year 2024. 
-- For each month, display the month name, total number of orders, total revenue, 
-- and the running total of revenue (cumulative revenue from January to that month).
-- Expected to show monthly and cumulative revenue
--
-- Logic: This requires a Window Function (SUM(...) OVER (ORDER BY ...)).
-- Trap: Sorting by Month Name (January, February) alphabetically puts "April" first.
-- Solution: We must group/sort by the Month Number (1, 2) but display the Month Name.
-- MySQL Syntax: Use MONTHNAME() for month name, MONTH() for month number, YEAR() for year.

SELECT 
    month_name,
    total_orders,
    monthly_revenue,
    SUM(monthly_revenue) OVER (
        ORDER BY month_num
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_revenue
FROM (
    SELECT
        MONTHNAME(o.order_date) AS month_name,
        MONTH(o.order_date) AS month_num,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total_amount) AS monthly_revenue
    FROM 
        orders o
    WHERE 
        YEAR(o.order_date) = 2024
    GROUP BY 
        MONTH(o.order_date), MONTHNAME(o.order_date)
) AS monthly_data
ORDER BY 
    month_num;

