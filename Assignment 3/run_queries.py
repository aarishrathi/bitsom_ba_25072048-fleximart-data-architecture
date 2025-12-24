"""
Script to run and display results of business queries
"""

import mysql.connector
from mysql.connector import Error
import os
from getpass import getpass

# Database configuration
# Password can be provided via MYSQL_PASSWORD environment variable
# Otherwise, you will be prompted securely for the password
def get_db_config():
    """Get database configuration with secure password handling."""
    password = os.getenv('MYSQL_PASSWORD')
    if password is None:
        password = getpass("Enter MySQL password: ")
    
    return {
        "host": os.getenv('MYSQL_HOST', 'localhost'),
        "database": os.getenv('MYSQL_DATABASE', 'fleximart'),
        "user": os.getenv('MYSQL_USER', 'root'),
        "password": password,
        "port": int(os.getenv('MYSQL_PORT', '3306'))
    }

DB_CONFIG = get_db_config()

def get_connection():
    """Create and return a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

def run_query(query_name, query_sql):
    """Execute a query and display results."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print(f"\n{'='*80}")
        print(f"{query_name}")
        print(f"{'='*80}")
        
        cursor.execute(query_sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        if not results:
            print("No results found.")
        else:
            # Print column headers
            print("\n" + " | ".join(f"{col:20}" for col in columns))
            print("-" * 80)
            
            # Print rows
            for row in results:
                print(" | ".join(f"{str(val):20}" for val in row))
            
            print(f"\nTotal rows: {len(results)}")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error executing query: {e}")

# Query 1: Customer Purchase History
query1 = """
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
"""

# Query 2: Product Sales Analysis
query2 = """
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
"""

# Query 3: Monthly Sales Trend
query3 = """
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
"""

if __name__ == "__main__":
    print("Running Business Queries for FlexiMart Database")
    print("=" * 80)
    
    run_query("Query 1: Customer Purchase History", query1)
    run_query("Query 2: Product Sales Analysis", query2)
    run_query("Query 3: Monthly Sales Trend", query3)
    
    print("\n" + "="*80)
    print("All queries completed!")

