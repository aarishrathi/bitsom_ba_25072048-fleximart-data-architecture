"""
ETL Pipeline for FlexiMart Data Processing

This script performs Extract, Transform, and Load (ETL) operations:
1. Extracts data from CSV files (customers, products, sales)
2. Transforms data by cleaning, standardizing, and handling missing values
3. Loads cleaned data into MySQL database

The pipeline processes three CSV files and creates normalized database tables.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from collections import defaultdict
import numpy as np
import sys
import os
from getpass import getpass

# ==============================
# DATABASE CONFIGURATION
# ==============================
# Connection settings for MySQL database
# Password can be provided via MYSQL_PASSWORD environment variable
# Otherwise, you will be prompted securely for the password
def get_db_config():
    """Get database configuration with secure password handling."""
    password = os.getenv('MYSQL_PASSWORD')
    if password is None:
        password = getpass("Enter MySQL password: ")
    
    return {
        "host": os.getenv('MYSQL_HOST', 'localhost'),      # Database server address
        "database": os.getenv('MYSQL_DATABASE', 'fleximart'),  # Database name
        "user": os.getenv('MYSQL_USER', 'root'),           # MySQL username
        "password": password,                              # MySQL password (from env or prompt)
        "port": int(os.getenv('MYSQL_PORT', '3306'))      # MySQL port (default is 3306)
    }

DB_CONFIG = get_db_config()

# ==============================
# DATA QUALITY METRICS TRACKER
# ==============================
# This class tracks statistics about data processing:
# - How many records were read from each file
# - How many duplicates were removed
# - How many missing values were filled or dropped
# - How many records were successfully loaded into the database
class DataQualityMetrics:
    def __init__(self):
        # Dictionary to store metrics for each file
        self.metrics = defaultdict(lambda: defaultdict(int))
        # Dictionary to track reasons for dropping records
        self.drop_reasons = defaultdict(lambda: defaultdict(int))

    def read(self, file, n): 
        """Track number of records read from a file"""
        self.metrics[file]["records_read"] += n
    
    def dup(self, file, n): 
        """Track number of duplicate records removed"""
        self.metrics[file]["duplicates_removed"] += n
    
    def filled(self, file, n): 
        """Track number of missing values filled with defaults"""
        self.metrics[file]["missing_values_filled"] += n
    
    def loaded(self, file, n): 
        """Track number of records successfully loaded into database"""
        self.metrics[file]["records_loaded"] += n
    
    def dropped(self, file, reason, n):
        """Track number of records dropped and the reason"""
        self.metrics[file]["rows_dropped"] += n
        self.drop_reasons[file][reason] += n

# Global metrics object to track statistics across all processing steps
METRICS = DataQualityMetrics()

# ==============================
# HELPER FUNCTIONS
# ==============================

def get_connection():
    """
    Create and return a connection to the MySQL database.
    This function uses the DB_CONFIG settings to establish the connection.
    """
    return mysql.connector.connect(**DB_CONFIG)

def create_database_schema():
    """
    Create the database and all required tables if they don't exist.
    
    This function:
    1. Creates the database if it doesn't exist
    2. Creates all tables (customers, products, orders, order_items) with their schemas
    3. Sets up foreign key relationships
    
    This makes the pipeline self-contained - it builds its own infrastructure
    before running the ETL process.
    """
    print("Creating database schema...")
    
    # First, connect without specifying database to create it if needed
    conn_no_db = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )
    cur_no_db = conn_no_db.cursor()
    
    # Create database if it doesn't exist
    cur_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn_no_db.commit()
    cur_no_db.close()
    conn_no_db.close()
    
    # Now connect to the database to create tables
    conn = get_connection()
    cur = conn.cursor()
    
    # SQL schema statements - using exact schema as specified (without IF NOT EXISTS for file)
    schema_statements_file = [
        "-- Database: fleximart\n",
        "\n",
        "CREATE TABLE customers (\n",
        "    customer_id INT PRIMARY KEY AUTO_INCREMENT,\n",
        "    first_name VARCHAR(50) NOT NULL,\n",
        "    last_name VARCHAR(50) NOT NULL,\n",
        "    email VARCHAR(100) UNIQUE NOT NULL,\n",
        "    phone VARCHAR(20),\n",
        "    city VARCHAR(50),\n",
        "    registration_date DATE\n",
        ");\n",
        "\n",
        "CREATE TABLE products (\n",
        "    product_id INT PRIMARY KEY AUTO_INCREMENT,\n",
        "    product_name VARCHAR(100) NOT NULL,\n",
        "    category VARCHAR(50) NOT NULL,\n",
        "    price DECIMAL(10,2) NOT NULL,\n",
        "    stock_quantity INT DEFAULT 0\n",
        ");\n",
        "\n",
        "CREATE TABLE orders (\n",
        "    order_id INT PRIMARY KEY AUTO_INCREMENT,\n",
        "    customer_id INT NOT NULL,\n",
        "    order_date DATE NOT NULL,\n",
        "    total_amount DECIMAL(10,2) NOT NULL,\n",
        "    status VARCHAR(20) DEFAULT 'Pending',\n",
        "    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)\n",
        ");\n",
        "\n",
        "CREATE TABLE order_items (\n",
        "    order_item_id INT PRIMARY KEY AUTO_INCREMENT,\n",
        "    order_id INT NOT NULL,\n",
        "    product_id INT NOT NULL,\n",
        "    quantity INT NOT NULL,\n",
        "    unit_price DECIMAL(10,2) NOT NULL,\n",
        "    subtotal DECIMAL(10,2) NOT NULL,\n",
        "    FOREIGN KEY (order_id) REFERENCES orders(order_id),\n",
        "    FOREIGN KEY (product_id) REFERENCES products(product_id)\n",
        ");\n",
        "\n"
    ]
    
    # SQL schema statements for execution - using IF NOT EXISTS for idempotency
    schema_statements_exec = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT PRIMARY KEY AUTO_INCREMENT,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            city VARCHAR(50),
            registration_date DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY AUTO_INCREMENT,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock_quantity INT DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id INT NOT NULL,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INT PRIMARY KEY AUTO_INCREMENT,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
    ]
    
    # Execute each CREATE TABLE statement
    for statement in schema_statements_exec:
        try:
            cur.execute(statement)
            conn.commit()
        except Error as e:
            print(f"Error creating table: {e}")
            raise
    
    # Write schema to SQL file
    sql_filename = "fleximart_schema.sql"
    with open(sql_filename, "w") as f:
        f.writelines(schema_statements_file)
    
    cur.close()
    conn.close()
    print(f"Database schema created successfully.")
    print(f"Schema exported to {sql_filename}")

def safe_value(val):
    """
    Convert NaN/NaT values to None for database insertion.
    
    Args:
        val: Value that might be NaN, NaT, or a valid value
    
    Returns:
        None if value is NaN/NaT, otherwise the original value
    """
    if pd.isna(val):
        return None
    return val

def clean_date_series(series):
    """
    Robustly parses mixed date formats in a pandas Series.
    
    Strategy: 
    1. Try ISO (YYYY-MM-DD) first (Most common)
    2. Try Day-First (DD/MM/YYYY) for remaining NaTs
    3. Try Month-First (MM-DD-YYYY) for remaining NaTs
    
    This approach minimizes data loss by trying multiple common formats
    before giving up on a date value.
    
    Args:
        series: pandas Series containing date strings in various formats
    
    Returns:
        pandas Series with date objects (YYYY-MM-DD format) or NaT for unparseable dates
    """
    # 1. Try standard YYYY-MM-DD first (most common format)
    dates = pd.to_datetime(series, format='%Y-%m-%d', errors='coerce')
    
    # 2. Fill NaTs with DD/MM/YYYY (e.g., 15/01/2024, common in Indian/UK format)
    mask = dates.isna()
    dates[mask] = pd.to_datetime(series[mask], format='%d/%m/%Y', errors='coerce')
    
    # 3. Fill remaining NaTs with MM-DD-YYYY (e.g., 01-22-2024, US format)
    mask = dates.isna()
    dates[mask] = pd.to_datetime(series[mask], format='%m-%d-%Y', errors='coerce')
    
    # 4. Try MM/DD/YYYY format as well
    mask = dates.isna()
    dates[mask] = pd.to_datetime(series[mask], format='%m/%d/%Y', errors='coerce')
    
    # Final cleanup: Ensure everything is proper date object (removes time component)
    return dates.dt.date

def clean_phone(phone):
    """
    Standardize phone numbers to the format: +91-XXXXXXXXXX
    
    This function:
    - Handles missing/empty phone numbers (returns None)
    - Converts scientific notation (e.g., 9.876e9) to regular numbers
    - Extracts the last 10 digits (Indian phone numbers)
    - Formats as +91-XXXXXXXXXX
    
    Args:
        phone: Raw phone number (can be string, number, or NaN)
    
    Returns:
        Standardized phone number string (e.g., "+91-9876543210") or None
    """
    if pd.isna(phone): 
        return None
    try:
        # Convert to string, handling scientific notation (e.g., 9.876e9 -> 9876000000)
        phone_str = str(int(float(phone)))
        # Extract last 10 digits and format as +91-XXXXXXXXXX
        if len(phone_str) >= 10:
            return "+91-" + phone_str[-10:]
    except:
        pass
    return None


# ==============================
# 1. CUSTOMERS DATA PROCESSING
# ==============================
def process_customers():
    """
    Extract, transform, and load customer data from CSV file.
    
    Steps:
    1. Read customer data from CSV file
    2. Remove duplicate records (based on email)
    3. Drop records with missing email addresses (required field)
    4. Standardize phone numbers and dates
    5. Load data into database and create ID mapping
    
    Returns:
        Dictionary mapping old customer IDs (from CSV) to new database IDs
        Example: {'C001': 1, 'C002': 2, ...}
    """
    file = "../data/customers_raw.csv"
    print(f"Processing {file}...")
    
    # Step 1: Extract - Read data from CSV file
    df = pd.read_csv(file)
    METRICS.read(file, len(df))

    # Step 2: Transform - Remove duplicate records
    # Keep the first occurrence when duplicate emails are found
    before = len(df)
    df = df.drop_duplicates(subset=['email'], keep='first')
    METRICS.dup(file, before - len(df))

    # Step 3: Transform - Handle missing values
    # Email is a required field, so drop records with missing emails
    missing = df['email'].isna()
    METRICS.dropped(file, "missing_email", missing.sum())
    df = df[~missing]

    # Step 4: Transform - Standardize data formats
    # Convert phone numbers to +91-XXXXXXXXXX format
    df['phone'] = df['phone'].apply(clean_phone)
    
    # Convert dates to YYYY-MM-DD format using robust multi-format parsing
    # Note: registration_date is nullable in schema, so NULL is acceptable for invalid dates
    # Invalid/unparseable dates are stored as NULL and counted as "missing values handled"
    # (The row is still loaded, but with NULL date - this is compliant with schema)
    date_series = clean_date_series(df['registration_date'])
    
    # Convert date objects to YYYY-MM-DD strings for database storage (vectorized)
    # Python date objects convert to YYYY-MM-DD format when converted to string
    # Replace NaT (unparseable dates) with None for database compatibility
    df['registration_date'] = date_series.apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)
    
    # Track missing/invalid dates - these are stored as NULL (not dropped)
    # This is counted as "missing values handled" in the report
    invalid_dates = df['registration_date'].isna().sum()
    if invalid_dates > 0:
        # Count as missing values handled (stored as NULL, not dropped)
        METRICS.filled(file, invalid_dates)

    # Step 5: Load - Insert data into database
    conn = get_connection()
    cur = conn.cursor()
    
    # Create mapping: old CSV ID (e.g., 'C001') -> new database ID (e.g., 1)
    # This mapping is needed to link sales records to customers later
    id_map = {} 
    
    insert_query = """
        INSERT INTO customers (first_name, last_name, email, phone, city, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # Process each customer record
    for _, row in df.iterrows():
        try:
            # Insert customer into database
            # Convert NaN values to None for database compatibility
            cur.execute(insert_query, (
                safe_value(row['first_name']), 
                safe_value(row['last_name']), 
                safe_value(row['email']), 
                safe_value(row['phone']), 
                safe_value(row['city']), 
                safe_value(row['registration_date'])
            ))
            # Get the auto-generated ID from database
            new_id = cur.lastrowid
            # Track the metric - if execute() succeeded without exception, the record was loaded
            METRICS.loaded(file, 1)
            # Store mapping: old CSV ID -> new database ID (if we got a valid ID)
            if new_id:
                id_map[row['customer_id']] = new_id
        except Error as e:
            # Handle duplicate email (if record already exists in database)
            if 'Duplicate entry' in str(e) and 'email' in str(e):
                # Fetch the existing customer's ID
                cur.execute("SELECT customer_id FROM customers WHERE email = %s", (row['email'],))
                result = cur.fetchone()
                if result:
                    # Use existing ID for the mapping
                    id_map[row['customer_id']] = result[0]
            else:
                print(f"Error loading customer {row['email']}: {e}")
            continue

    # Save all changes to database
    conn.commit()
    cur.close()
    conn.close()
    return id_map

# ==============================
# 2. PRODUCTS DATA PROCESSING
# ==============================
def process_products():
    """
    Extract, transform, and load product data from CSV file.
    
    Steps:
    1. Read product data from CSV file
    2. Remove duplicate records (based on product_id)
    3. Standardize category names to Title Case
    4. Handle missing stock quantities (fill with 0)
    5. Drop records with missing prices (required field)
    6. Load data into database and create ID mapping
    
    Returns:
        Dictionary mapping old product IDs (from CSV) to new database IDs
        Example: {'P001': 1, 'P002': 2, ...}
    """
    file = "../data/products_raw.csv"
    print(f"Processing {file}...")
    
    # Step 1: Extract - Read data from CSV file
    df = pd.read_csv(file)
    METRICS.read(file, len(df))

    # Step 2: Transform - Remove duplicate records
    # Keep the first occurrence when duplicate product_ids are found
    before = len(df)
    df = df.drop_duplicates(subset=['product_id'], keep='first')
    METRICS.dup(file, before - len(df))

    # Step 3: Transform - Standardize category names
    # Convert to Title Case: "electronics" -> "Electronics", "FASHION" -> "Fashion"
    df['category'] = df['category'].astype(str).str.title()

    # Step 4: Transform - Handle missing stock quantities
    # Fill missing stock with 0 (default value)
    null_stock = df['stock_quantity'].isna().sum()
    df['stock_quantity'] = df['stock_quantity'].fillna(0)
    METRICS.filled(file, null_stock)

    # Step 5: Transform - Handle missing prices
    # Price is a required field, so drop records with missing prices
    # (We don't guess prices as per business rule)
    missing_price = df['price'].isna()
    METRICS.dropped(file, "missing_price", missing_price.sum())
    df = df[~missing_price]

    # Step 6: Load - Insert data into database
    conn = get_connection()
    cur = conn.cursor()
    
    # Create mapping: old CSV ID (e.g., 'P001') -> new database ID (e.g., 1)
    # This mapping is needed to link sales records to products later
    id_map = {}

    insert_query = """
        INSERT INTO products (product_name, category, price, stock_quantity)
        VALUES (%s, %s, %s, %s)
    """

    # Process each product record
    for _, row in df.iterrows():
        # Insert product into database
        # Convert NaN values to None for database compatibility
        cur.execute(insert_query, (
            safe_value(row['product_name']), 
            safe_value(row['category']), 
            safe_value(row['price']), 
            safe_value(row['stock_quantity'])
        ))
        # Get the auto-generated ID from database
        new_id = cur.lastrowid
        # Store mapping: old CSV ID -> new database ID
        id_map[row['product_id']] = new_id
        METRICS.loaded(file, 1)

    # Save all changes to database
    conn.commit()
    cur.close()
    conn.close()
    return id_map

# ==============================
# 3. SALES DATA PROCESSING (ORDERS + ORDER ITEMS)
# ==============================
def process_sales(cust_map, prod_map):
    """
    Extract, transform, and load sales data from CSV file.
    
    This function processes sales transactions and creates:
    - Order records (one per transaction)
    - Order item records (one per product in each transaction)
    
    Steps:
    1. Read sales data from CSV file
    2. Remove duplicate records
    3. Map old customer/product IDs to new database IDs
    4. Drop orphan records (sales with invalid customer/product references)
    5. Standardize transaction dates
    6. Group transactions into orders and order items
    7. Load data into database
    
    Args:
        cust_map: Dictionary mapping old customer IDs to new database IDs
        prod_map: Dictionary mapping old product IDs to new database IDs
    """
    file = "../data/sales_raw.csv"
    print(f"Processing {file}...")
    
    # Step 1: Extract - Read data from CSV file
    df = pd.read_csv(file)
    METRICS.read(file, len(df))

    # Step 2: Transform - Remove duplicate records
    # Remove rows that are exactly the same (all columns match)
    before = len(df)
    df = df.drop_duplicates()
    METRICS.dup(file, before - len(df))

    # Step 3: Transform - Map old IDs to new database IDs
    # Convert CSV customer IDs (e.g., 'C001') to database customer IDs (e.g., 1)
    df['db_customer_id'] = df['customer_id'].map(cust_map)
    # Convert CSV product IDs (e.g., 'P001') to database product IDs (e.g., 1)
    df['db_product_id'] = df['product_id'].map(prod_map)

    # Step 4: Transform - Handle orphan records
    # Drop sales records where customer or product was not found/loaded
    # (These are called "orphan" records because they reference non-existent data)
    orphans = df[df['db_customer_id'].isna() | df['db_product_id'].isna()]
    METRICS.dropped(file, "orphan_record_missing_parent", len(orphans))
    
    # Keep only valid sales records (with valid customer and product references)
    valid_sales = df.dropna(subset=['db_customer_id', 'db_product_id']).copy()

    # Step 5: Transform - Standardize transaction dates using robust multi-format parsing
    # IMPORTANT: order_date is NOT NULL in schema, so records with invalid dates MUST be dropped
    # Invalid/unparseable dates cannot be stored in order_date column
    # Using robust clean_date_series function to minimize data loss by trying multiple formats
    date_series = clean_date_series(valid_sales['transaction_date'])
    
    # Convert date objects to YYYY-MM-DD strings for database storage
    # Python date objects convert to YYYY-MM-DD format when converted to string
    valid_sales['transaction_date'] = date_series.apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)
    
    # Check if any dates failed to parse after all format attempts
    failed_dates = valid_sales['transaction_date'].isna().sum()
    if failed_dates > 0:
        print(f"⚠️ Warning: {failed_dates} transaction dates could not be parsed and will be dropped.")
        METRICS.dropped(file, "invalid_transaction_date", failed_dates)
        # Drop records with invalid/missing transaction dates (order_date is NOT NULL constraint)
        valid_sales = valid_sales[valid_sales['transaction_date'].notna()].copy()

    # Step 6: Load - Insert data into database
    conn = get_connection()
    cur = conn.cursor()
    
    # Group sales by transaction_id to create orders
    # Each transaction becomes one order with multiple order items
    grouped = valid_sales.groupby('transaction_id')
    
    items_loaded = 0

    # Process each transaction/order
    for trans_id, group in grouped:
        # Get order-level information (same for all items in this transaction)
        customer_id = group.iloc[0]['db_customer_id']
        order_date = group.iloc[0]['transaction_date']
        
        # Calculate total amount for this order (sum of all items)
        total_amt = (group['quantity'] * group['unit_price']).sum()

        # Insert order record (one per transaction)
        # Note: order_date is guaranteed to be valid (not None) because we dropped
        # all records with invalid dates in Step 5 above (order_date is NOT NULL in schema)
        cur.execute("""
            INSERT INTO orders (customer_id, order_date, total_amount, status)
            VALUES (%s, %s, %s, 'Completed')
        """, (int(customer_id), order_date, float(total_amt)))
        
        # Get the auto-generated order ID
        new_order_id = cur.lastrowid

        # Prepare order items (one per product in this transaction)
        item_rows = []
        for _, row in group.iterrows():
            # Calculate subtotal for this item
            subtotal = row['quantity'] * row['unit_price']
            item_rows.append((
                new_order_id,                    # Link to the order
                int(row['db_product_id']),      # Product ID
                int(row['quantity']),            # Quantity purchased
                float(row['unit_price']),        # Price per unit
                float(subtotal)                  # Total for this item
            ))

        # Insert each order item into database
        for item_row in item_rows:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, item_row)
        
        items_loaded += len(item_rows)

    # Save all changes to database
    conn.commit()
    METRICS.loaded(file, items_loaded)
    cur.close()
    conn.close()

# ==============================
# REPORT GENERATION
# ==============================
def generate_report():
    """
    Generate a data quality report showing processing statistics.
    
    The report includes for each file:
    - Number of records processed (read from CSV)
    - Number of duplicates removed
    - Number of missing values handled (filled or dropped)
    - Number of records successfully loaded into database
    - Reasons for dropping records
    
    Date Handling:
    - registration_date (nullable): Invalid dates are stored as NULL and counted as "missing values handled"
    - order_date (NOT NULL): Records with invalid dates are dropped and reported as "invalid_transaction_date"
    
    The report is saved to 'data_quality_report.txt'
    """
    with open("data_quality_report.txt", "w") as f:
        f.write("FLEXIMART ETL EXECUTION REPORT\n")
        f.write("==============================\n\n")
        f.write("DATE HANDLING POLICY:\n")
        f.write("- registration_date (nullable): Invalid/unparseable dates stored as NULL\n")
        f.write("- order_date (NOT NULL): Records with invalid dates are dropped\n")
        f.write("All valid dates are converted to YYYY-MM-DD format.\n\n")
        
        # Generate report for each processed file
        for file, stats in METRICS.metrics.items():
            f.write(f"FILE: {file}\n")
            f.write("-" * 50 + "\n")
            
            # Number of records read from CSV file
            f.write(f"  Records Processed:        {stats['records_read']}\n")
            
            # Number of duplicate records removed
            f.write(f"  Duplicates Removed:       {stats['duplicates_removed']}\n")
            
            # Total missing values handled (both filled and dropped)
            total_missing = stats['missing_values_filled'] + stats['rows_dropped']
            f.write(f"  Missing Values Handled:   {total_missing}\n")
            f.write(f"    - Filled with defaults: {stats['missing_values_filled']}\n")
            f.write(f"    - Dropped:              {stats['rows_dropped']}\n")
            
            # Number of records successfully loaded into database
            f.write(f"  Records Loaded:           {stats['records_loaded']}\n")
            
            # Calculate and display success percentage
            if stats['records_read'] > 0:
                success_rate = (stats['records_loaded'] / stats['records_read']) * 100
                f.write(f"  Success Rate:             {success_rate:.2f}%\n")
            else:
                f.write(f"  Success Rate:             N/A (no records processed)\n")
            
            # Show detailed reasons for dropping records
            if METRICS.drop_reasons[file]:
                f.write("  Drop Reasons:\n")
                for reason, count in METRICS.drop_reasons[file].items():
                    f.write(f"    * {reason}: {count}\n")
            f.write("\n")

# ==============================
# MAIN EXECUTION
# ==============================
if __name__ == "__main__":
    """
    Main execution block - runs the complete ETL pipeline.
    
    Execution order:
    1. Create database schema (creates database and tables if they don't exist)
    2. Process customers first (creates customer ID mapping)
    3. Process products second (creates product ID mapping)
    4. Process sales last (uses customer and product mappings)
    5. Generate and save data quality report
    
    Note: The order matters because sales records need valid customer
    and product references, which are created in steps 2 and 3.
    """
    
    # Step 0: Create database schema (must run before ETL process)
    # This ensures all tables exist before attempting to insert data
    create_database_schema()
    
    # Optional: Clear all tables before running (uncomment to reset database)
    # This is useful for testing, but should be commented out in production
    # conn = get_connection()
    # cur = conn.cursor()
    # cur.execute("TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE;")
    # conn.commit()
    # conn.close()

    # Step 1: Process customers
    # Returns a dictionary mapping old customer IDs to new database IDs
    cust_map = process_customers()

    # Step 2: Process products
    # Returns a dictionary mapping old product IDs to new database IDs
    prod_map = process_products()

    # Step 3: Process sales
    # Uses the customer and product mappings to link sales to valid records
    process_sales(cust_map, prod_map)
    
    # Step 4: Generate and save the data quality report
    generate_report()
    print("ETL Pipeline Completed. Check data_quality_report.txt")
