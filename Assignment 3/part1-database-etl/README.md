# Part 1: Database ETL Pipeline

## Overview

This section implements a comprehensive ETL (Extract, Transform, Load) pipeline for processing raw customer, product, and sales data from CSV files into a normalized MySQL database. The pipeline includes robust data quality checks, handles missing values, removes duplicates, and standardizes data formats.

## Files

- **etl_pipeline.py**: Main ETL script that processes CSV files and loads data into MySQL
- **schema_documentation.md**: Complete documentation of the database schema including entity descriptions and relationships
- **business_queries.sql**: SQL queries answering key business questions
- **data_quality_report.txt**: Generated report showing data processing statistics (created after running ETL)
- **requirements.txt**: Python dependencies

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MySQL connection (optional):
   - The script will prompt for MySQL password when run
   - Alternatively, set environment variables:
     ```bash
     export MYSQL_HOST=localhost
     export MYSQL_USER=root
     export MYSQL_PASSWORD=your_password
     export MYSQL_DATABASE=fleximart
     export MYSQL_PORT=3306
     ```

3. Create MySQL database:
```bash
mysql -u root -p -e "CREATE DATABASE fleximart;"
```

4. Run the ETL pipeline:
```bash
python etl_pipeline.py
```

The script will:
- Prompt for MySQL password (if not set via environment variable)
- Create the database schema (tables: customers, products, orders, order_items)
- Process customer data from `../data/customers_raw.csv`
- Process product data from `../data/products_raw.csv`
- Process sales data from `../data/sales_raw.csv`
- Generate `data_quality_report.txt` with processing statistics

4. Execute business queries:
```bash
mysql -u root -p fleximart < business_queries.sql
```

## Database Schema

The normalized schema consists of four main tables:
- **customers**: Customer information and personal details
- **products**: Product catalog with pricing and inventory
- **orders**: Order transaction records
- **order_items**: Individual items within each order

See `schema_documentation.md` for detailed entity descriptions and relationships.

## Data Quality Features

- Duplicate removal based on business rules (email for customers, product_id for products)
- Missing value handling (filling defaults where appropriate, dropping invalid records)
- Date format standardization (handles multiple input formats: YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY)
- Phone number standardization (formats to +91-XXXXXXXXXX)
- Orphan record detection (drops sales records with invalid customer/product references)

