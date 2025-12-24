-- Warehouse Data Population Script
-- This script populates the FlexiMart Data Warehouse with sample data

-- ============================================
-- 1. DIM_DATE: 30 dates (January-February 2024)
-- ============================================
-- Includes both weekdays and weekends

INSERT INTO dim_date (date_key, full_date, day_of_week, day_of_month, month, month_name, quarter, year, is_weekend) VALUES
(20240101, '2024-01-01', 'Monday', 1, 1, 'January', 'Q1', 2024, false),
(20240102, '2024-01-02', 'Tuesday', 2, 1, 'January', 'Q1', 2024, false),
(20240103, '2024-01-03', 'Wednesday', 3, 1, 'January', 'Q1', 2024, false),
(20240104, '2024-01-04', 'Thursday', 4, 1, 'January', 'Q1', 2024, false),
(20240105, '2024-01-05', 'Friday', 5, 1, 'January', 'Q1', 2024, false),
(20240106, '2024-01-06', 'Saturday', 6, 1, 'January', 'Q1', 2024, true),
(20240107, '2024-01-07', 'Sunday', 7, 1, 'January', 'Q1', 2024, true),
(20240108, '2024-01-08', 'Monday', 8, 1, 'January', 'Q1', 2024, false),
(20240109, '2024-01-09', 'Tuesday', 9, 1, 'January', 'Q1', 2024, false),
(20240110, '2024-01-10', 'Wednesday', 10, 1, 'January', 'Q1', 2024, false),
(20240111, '2024-01-11', 'Thursday', 11, 1, 'January', 'Q1', 2024, false),
(20240112, '2024-01-12', 'Friday', 12, 1, 'January', 'Q1', 2024, false),
(20240113, '2024-01-13', 'Saturday', 13, 1, 'January', 'Q1', 2024, true),
(20240114, '2024-01-14', 'Sunday', 14, 1, 'January', 'Q1', 2024, true),
(20240115, '2024-01-15', 'Monday', 15, 1, 'January', 'Q1', 2024, false),
(20240116, '2024-01-16', 'Tuesday', 16, 1, 'January', 'Q1', 2024, false),
(20240117, '2024-01-17', 'Wednesday', 17, 1, 'January', 'Q1', 2024, false),
(20240118, '2024-01-18', 'Thursday', 18, 1, 'January', 'Q1', 2024, false),
(20240119, '2024-01-19', 'Friday', 19, 1, 'January', 'Q1', 2024, false),
(20240120, '2024-01-20', 'Saturday', 20, 1, 'January', 'Q1', 2024, true),
(20240121, '2024-01-21', 'Sunday', 21, 1, 'January', 'Q1', 2024, true),
(20240122, '2024-01-22', 'Monday', 22, 1, 'January', 'Q1', 2024, false),
(20240123, '2024-01-23', 'Tuesday', 23, 1, 'January', 'Q1', 2024, false),
(20240124, '2024-01-24', 'Wednesday', 24, 1, 'January', 'Q1', 2024, false),
(20240125, '2024-01-25', 'Thursday', 25, 1, 'January', 'Q1', 2024, false),
(20240126, '2024-01-26', 'Friday', 26, 1, 'January', 'Q1', 2024, false),
(20240127, '2024-01-27', 'Saturday', 27, 1, 'January', 'Q1', 2024, true),
(20240128, '2024-01-28', 'Sunday', 28, 1, 'January', 'Q1', 2024, true),
(20240129, '2024-01-29', 'Monday', 29, 1, 'January', 'Q1', 2024, false),
(20240201, '2024-02-01', 'Thursday', 1, 2, 'February', 'Q1', 2024, false);

-- ============================================
-- 2. DIM_PRODUCT: 15 products across 3 categories
-- ============================================
-- Prices range from ₹100 to ₹100,000

INSERT INTO dim_product (product_id, product_name, category, subcategory, unit_price) VALUES
-- Electronics Category (5 products)
('P001', 'Samsung Galaxy S24 Ultra', 'Electronics', 'Smartphones', 99999.00),
('P002', 'Apple iPhone 15 Pro', 'Electronics', 'Smartphones', 89999.00),
('P003', 'Sony WH-1000XM5 Headphones', 'Electronics', 'Audio', 24999.00),
('P004', 'Dell XPS 15 Laptop', 'Electronics', 'Laptops', 89999.00),
('P005', 'Canon EOS R6 Camera', 'Electronics', 'Cameras', 99999.00),

-- Fashion Category (5 products)
('P006', 'Nike Air Max 270', 'Fashion', 'Footwear', 8999.00),
('P007', 'Levi\'s 501 Jeans', 'Fashion', 'Clothing', 2999.00),
('P008', 'Zara Winter Jacket', 'Fashion', 'Clothing', 4999.00),
('P009', 'Ray-Ban Aviator Sunglasses', 'Fashion', 'Accessories', 12999.00),
('P010', 'Adidas Running Shoes', 'Fashion', 'Footwear', 5999.00),

-- Home & Kitchen Category (5 products)
('P011', 'Instant Pot Pressure Cooker', 'Home & Kitchen', 'Appliances', 8999.00),
('P012', 'Dyson V15 Vacuum Cleaner', 'Home & Kitchen', 'Appliances', 49999.00),
('P013', 'KitchenAid Stand Mixer', 'Home & Kitchen', 'Appliances', 34999.00),
('P014', 'Bamboo Cutting Board Set', 'Home & Kitchen', 'Cookware', 299.00),
('P015', 'Stainless Steel Cookware Set', 'Home & Kitchen', 'Cookware', 5999.00);

-- ============================================
-- 3. DIM_CUSTOMER: 12 customers across 4 cities
-- ============================================

INSERT INTO dim_customer (customer_id, customer_name, city, state, customer_segment) VALUES
-- Mumbai, Maharashtra (3 customers)
('C001', 'Rajesh Kumar', 'Mumbai', 'Maharashtra', 'VIP'),
('C002', 'Priya Sharma', 'Mumbai', 'Maharashtra', 'Returning'),
('C003', 'Amit Patel', 'Mumbai', 'Maharashtra', 'New'),

-- Delhi, Delhi (3 customers)
('C004', 'Anjali Singh', 'Delhi', 'Delhi', 'VIP'),
('C005', 'Vikram Mehta', 'Delhi', 'Delhi', 'Returning'),
('C006', 'Sneha Gupta', 'Delhi', 'Delhi', 'New'),

-- Bangalore, Karnataka (3 customers)
('C007', 'Rahul Reddy', 'Bangalore', 'Karnataka', 'VIP'),
('C008', 'Kavita Nair', 'Bangalore', 'Karnataka', 'Returning'),
('C009', 'Arjun Iyer', 'Bangalore', 'Karnataka', 'New'),

-- Chennai, Tamil Nadu (3 customers)
('C010', 'Lakshmi Venkatesh', 'Chennai', 'Tamil Nadu', 'VIP'),
('C011', 'Suresh Raman', 'Chennai', 'Tamil Nadu', 'Returning'),
('C012', 'Meera Krishnan', 'Chennai', 'Tamil Nadu', 'New');

-- ============================================
-- 4. FACT_SALES: 40 sales transactions
-- ============================================
-- Realistic patterns: Higher sales on weekends, varied quantities
-- Note: product_key and customer_key will be auto-incremented starting from 1

INSERT INTO fact_sales (date_key, product_key, customer_key, quantity_sold, unit_price, discount_amount, total_amount) VALUES
-- Weekend Sales (Higher volume - Saturday, Jan 6)
(20240106, 1, 1, 1, 99999.00, 5000.00, 94999.00),
(20240106, 3, 2, 2, 24999.00, 2000.00, 47998.00),
(20240106, 6, 3, 1, 8999.00, 500.00, 8499.00),
(20240106, 9, 4, 1, 12999.00, 1000.00, 11999.00),
(20240106, 11, 5, 1, 8999.00, 0.00, 8999.00),

-- Weekend Sales (Sunday, Jan 7)
(20240107, 2, 6, 1, 89999.00, 10000.00, 79999.00),
(20240107, 7, 7, 3, 2999.00, 500.00, 8497.00),
(20240107, 10, 8, 2, 5999.00, 1000.00, 10998.00),
(20240107, 12, 9, 1, 49999.00, 5000.00, 44999.00),
(20240107, 15, 10, 1, 5999.00, 0.00, 5999.00),

-- Weekend Sales (Saturday, Jan 13)
(20240113, 4, 11, 1, 89999.00, 8000.00, 81999.00),
(20240113, 8, 12, 2, 4999.00, 500.00, 9498.00),
(20240113, 13, 1, 1, 34999.00, 3000.00, 31999.00),
(20240113, 14, 2, 4, 299.00, 0.00, 1196.00),
(20240113, 5, 3, 1, 99999.00, 10000.00, 89999.00),

-- Weekend Sales (Sunday, Jan 14)
(20240114, 1, 4, 1, 99999.00, 10000.00, 89999.00),
(20240114, 3, 5, 1, 24999.00, 2000.00, 22999.00),
(20240114, 6, 6, 2, 8999.00, 1000.00, 16998.00),
(20240114, 9, 7, 1, 12999.00, 0.00, 12999.00),
(20240114, 11, 8, 1, 8999.00, 500.00, 8499.00),

-- Weekend Sales (Saturday, Jan 20)
(20240120, 2, 9, 1, 89999.00, 5000.00, 84999.00),
(20240120, 7, 10, 2, 2999.00, 0.00, 5998.00),
(20240120, 10, 11, 1, 5999.00, 500.00, 5499.00),
(20240120, 12, 12, 1, 49999.00, 4000.00, 45999.00),
(20240120, 15, 1, 2, 5999.00, 1000.00, 10998.00),

-- Weekend Sales (Sunday, Jan 21)
(20240121, 4, 2, 1, 89999.00, 7000.00, 82999.00),
(20240121, 8, 3, 1, 4999.00, 0.00, 4999.00),
(20240121, 13, 4, 1, 34999.00, 2000.00, 32999.00),

-- Weekend Sales (Saturday, Jan 27)
(20240127, 1, 6, 1, 99999.00, 8000.00, 91999.00),
(20240127, 3, 7, 2, 24999.00, 3000.00, 46998.00),
(20240127, 6, 8, 1, 8999.00, 500.00, 8499.00),
(20240127, 9, 9, 1, 12999.00, 1000.00, 11999.00),

-- Weekend Sales (Sunday, Jan 28)
(20240128, 2, 10, 1, 89999.00, 9000.00, 80999.00),
(20240128, 7, 11, 4, 2999.00, 1000.00, 10996.00),
(20240128, 10, 12, 2, 5999.00, 500.00, 11498.00),
(20240128, 12, 1, 1, 49999.00, 5000.00, 44999.00),

-- Weekday Sales (Lower volume - Monday, Jan 8)
(20240108, 15, 2, 1, 5999.00, 0.00, 5999.00),
(20240108, 14, 3, 2, 299.00, 0.00, 598.00),

-- Weekday Sales (Tuesday, Jan 9)
(20240109, 11, 4, 1, 8999.00, 500.00, 8499.00),
(20240109, 13, 5, 1, 34999.00, 2000.00, 32999.00);

