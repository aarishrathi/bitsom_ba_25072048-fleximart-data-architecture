# Part 3: Data Warehouse - Star Schema Design

## Overview

This section implements a data warehouse using a star schema design optimized for analytical queries and business intelligence. The warehouse enables efficient OLAP (Online Analytical Processing) operations including drill-down analysis, roll-up aggregations, and multi-dimensional reporting.

## Files

- **star_schema_design.md**: Complete documentation of the star schema design including fact and dimension tables
- **warehouse_schema.sql**: SQL script to create the data warehouse schema (dimensions and fact table)
- **warehouse_data.sql**: SQL script to populate the data warehouse with sample data
- **analytics_queries.sql**: OLAP queries demonstrating business intelligence use cases

## Setup

1. Create the data warehouse database:
```bash
mysql -u root -p -e "CREATE DATABASE fleximart_dw;"
```

2. Create the warehouse schema:
```bash
mysql -u root -p fleximart_dw < warehouse_schema.sql
```

3. Load sample data:
```bash
mysql -u root -p fleximart_dw < warehouse_data.sql
```

4. Run analytics queries:
```bash
mysql -u root -p fleximart_dw < analytics_queries.sql
```

## Star Schema Structure

### Fact Table
- **fact_sales**: Transaction-level fact table containing sales measures (quantity, price, amounts)

### Dimension Tables
- **dim_date**: Date dimension with hierarchies (Year → Quarter → Month → Day)
- **dim_product**: Product dimension with category hierarchies
- **dim_customer**: Customer dimension with geographic attributes

## Key Features

- **Drill-Down Analysis**: Query sales from year to quarter to month level
- **Product Performance**: Analyze sales by product categories
- **Customer Segmentation**: Group customers by geographic regions
- **Time-Series Analysis**: Track sales trends over time
- **Multi-Dimensional Reporting**: Combine multiple dimensions in single queries

## Design Principles

- **Denormalized Structure**: Dimensions contain redundant data for query performance
- **Surrogate Keys**: Integer keys for efficient joins
- **Conformed Dimensions**: Reusable across multiple fact tables
- **Grain Definition**: One row per line item in fact table

See `star_schema_design.md` for detailed design documentation.

