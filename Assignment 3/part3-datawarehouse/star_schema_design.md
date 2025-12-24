# FlexiMart Data Warehouse: Star Schema Design

## Table of Contents
1. [Schema Overview](#section-1-schema-overview)
2. [Design Decisions](#section-2-design-decisions)
3. [Sample Data Flow](#section-3-sample-data-flow)

---

## Section 1: Schema Overview

This document outlines the Star Schema design for the FlexiMart Sales Analytics Data Warehouse. The design facilitates high-performance querying for business intelligence reports, specifically targeting sales trends, product performance, and customer behavior.

### FACT TABLE: `fact_sales`

**Grain:** One row per individual line item within a customer order.  
**Business Process:** Validated Sales Transactions (Completed Orders).  
**Type:** Transaction Fact Table

#### Primary Key
- Composite key: `(date_key, product_key, customer_key, order_id)`

#### Measures (Numeric Facts)
| Field Name | Data Type | Description |
|-----------|-----------|-------------|
| `quantity_sold` | INT | Number of units of the specific product purchased in this line item |
| `unit_price` | DECIMAL(10,2) | The price of the product at the exact moment of transaction |
| `gross_amount` | DECIMAL(12,2) | Calculated as `quantity_sold * unit_price` |
| `discount_amount` | DECIMAL(12,2) | Any promotional discount applied to this specific line item |
| `net_amount` | DECIMAL(12,2) | The final revenue recognized (`gross_amount - discount_amount`) |

#### Foreign Keys (Surrogate Keys)
| Field Name | Data Type | References | Description |
|------------|-----------|------------|-------------|
| `date_key` | INT | `dim_date.date_key` | Integer format: YYYYMMDD (e.g., 20240115) |
| `product_key` | INT | `dim_product.product_key` | Surrogate key linking to product dimension |
| `customer_key` | INT | `dim_customer.customer_key` | Surrogate key linking to customer dimension |
| `order_id` | VARCHAR(50) | - | Degenerate Dimension (Natural Key) retained for invoice lookup |

---

### DIMENSION TABLE: `dim_date`

**Purpose:** A Conformed Dimension enabling time-series analysis (Daily, Monthly, Quarterly, Yearly) across all business processes.  
**Type:** Static Dimension (pre-populated, rarely changes)

#### Primary Key
- `date_key` (INT): Surrogate Key in format YYYYMMDD

#### Attributes
| Field Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| `date_key` | INT (PK) | Surrogate Key (Integer format: YYYYMMDD) | 20240115 |
| `full_date` | DATE | The actual Date object | 2024-01-15 |
| `day_of_week` | VARCHAR(10) | Name of the day | "Monday" |
| `day_num_of_month` | INT | Day number (1-31) | 15 |
| `month_num` | INT | Month number (1-12) | 1 |
| `month_name` | VARCHAR(20) | Full month name | "January" |
| `quarter` | VARCHAR(2) | Fiscal Quarter | "Q1" |
| `year` | INT | The 4-digit year | 2024 |
| `is_weekend` | BOOLEAN | Boolean flag to easily filter weekday vs. weekend sales | false |

---

### DIMENSION TABLE: `dim_product`

**Purpose:** Stores descriptive attributes of products to analyze sales by category or brand.  
**Type:** SCD Type 2 (Slowly Changing Dimension) - Tracks historical changes in product attributes (e.g., if a product changes category).

#### Primary Key
- `product_key` (INT): Surrogate Key (Auto-increment Integer)

#### Attributes
| Field Name | Data Type | Description | Notes |
|------------|-----------|-------------|-------|
| `product_key` | INT (PK) | Surrogate Key (Auto-increment Integer) | Unique identifier |
| `product_id_natural` | VARCHAR(50) | The original ID from the source system | e.g., "P001", "ELEC001" |
| `product_name` | VARCHAR(200) | Full name of the product | e.g., "Samsung Galaxy S21 Ultra" |
| `category` | VARCHAR(50) | High-level classification | e.g., "Electronics", "Fashion" |
| `subcategory` | VARCHAR(50) | Granular classification | e.g., "Smartphones", "Clothing" |
| `current_price` | DECIMAL(10,2) | The current list price | May differ from historical `unit_price` in fact table |
| `stock_status` | VARCHAR(20) | Indicator of availability | e.g., "In Stock", "Out of Stock" |
| `effective_start_date` | DATE | Date when this version of the product record became active | SCD Type 2 tracking |
| `effective_end_date` | DATE | Date when this version expired (NULL if current) | NULL = current record |
| `is_current` | BOOLEAN | Boolean flag indicating the active record | true = current version |

**SCD Type 2 Behavior:** When a product attribute changes (e.g., category), a new row is inserted with a new `product_key`, updated attributes, and `is_current = true`. The old row's `effective_end_date` is set and `is_current = false`.

---

### DIMENSION TABLE: `dim_customer`

**Purpose:** Stores customer demographics to support segmentation and cohort analysis.  
**Type:** SCD Type 1 (Overwrites old data) - We assume we only care about the customer's *current* state (e.g., current city) for this analysis.

#### Primary Key
- `customer_key` (INT): Surrogate Key (Auto-increment Integer)

#### Attributes
| Field Name | Data Type | Description | Notes |
|------------|-----------|-------------|-------|
| `customer_key` | INT (PK) | Surrogate Key (Auto-increment Integer) | Unique identifier |
| `customer_id_natural` | VARCHAR(50) | The original ID from the source system | e.g., "C001", "U001" |
| `full_name` | VARCHAR(100) | Combined First and Last name | e.g., "John Doe" |
| `email` | VARCHAR(100) | Customer's contact email | Unique identifier |
| `city` | VARCHAR(50) | Current city of residence | e.g., "Mumbai", "Delhi" |
| `state` | VARCHAR(50) | State/Region (Derived from City mapping) | e.g., "Maharashtra" |
| `customer_segment` | VARCHAR(20) | Derived classification | e.g., "New", "VIP", "Returning" |
| `registration_date_key` | INT | Integer Key linking to `dim_date` for cohort analysis | Format: YYYYMMDD |

**SCD Type 1 Behavior:** When customer information changes (e.g., city), the existing record is updated in place. Historical accuracy is not maintained for customer attributes.

---

## Section 2: Design Decisions

### 1. Granularity Choice: Transaction Line-Item Level

**Decision:** Selected the **line-item grain** (one row per product per order) as the atomic level of detail.

**Rationale:**
- **Precision:** Enables analysis of specific product performance (e.g., "How many *Sony Headphones* sold on Fridays?"). If aggregated at the *Order* level, visibility into individual items within the basket would be lost.
- **Flexibility:** Atomic data is future-proof. We can always sum line items up to calculate Order Total or Daily Revenue, but we cannot break aggregated data back down if detailed insights are needed later.
- **Business Value:** Supports detailed product-level analytics, basket analysis, and cross-selling opportunities.

---

### 2. Surrogate Keys vs. Natural Keys

**Decision:** Use **Surrogate Keys** (e.g., `product_key`, an auto-incrementing integer) instead of Natural Keys (`P001`, `ELEC001`).

**Rationale:**
- **History Tracking (SCD):** If "Sony Headphones" changes category from "Audio" to "Electronics", we can keep *both* versions in `dim_product` with different `product_key`s but the same natural ID. This preserves historical accuracy in reports - sales from before the change link to the old category, and sales after link to the new category.
- **Performance:** Joining tables on integer columns (`INT`) is significantly faster in databases than joining on variable-length strings (`VARCHAR`). This becomes critical when processing millions of fact rows.
- **Independence:** Surrogate keys are independent of business rules, making the warehouse resilient to source system changes.

---

### 3. Support for Drill-Down and Roll-Up (OLAP Operations)

**Decision:** Design schema to natively support OLAP operations through dimension hierarchies.

**Implementation:**
- **Roll-Up:** Analysts can easily aggregate `fact_sales` measures up the hierarchy. For example, in `dim_date`, we can roll up from `day` → `month` → `quarter` → `year` using simple `GROUP BY` clauses.
- **Drill-Down:** Conversely, if a "Q4 Revenue" report shows a dip, an analyst can drill down by:
  - Adding `dim_product.category` to see if a specific product line caused the drop
  - Filtering by `dim_customer.city` to isolate regional issues
  - Breaking down by `dim_date.month_name` to identify the specific month

**Example Hierarchy:**
```
Year → Quarter → Month → Day
Category → Subcategory → Product
State → City → Customer
```

---

### 4. Slowly Changing Dimension (SCD) Strategy

**Decision:** Mixed SCD approach based on business requirements.

- **`dim_product` (SCD Type 2):** Tracks historical changes to preserve report accuracy. When a product's category changes, both versions are maintained.
- **`dim_customer` (SCD Type 1):** Overwrites old data since we only need current customer state for segmentation and cohort analysis.
- **`dim_date` (Static):** Pre-populated dimension that rarely changes.

---

## Section 3: Sample Data Flow

This example illustrates the transformation of a raw operational transaction into the normalized Star Schema format.

### 1. Source Operational Transaction (Raw Data)

*Captured in the e-commerce application (OLTP system)*

```
Order ID: #101
Date: 2024-01-15 14:30:00
Customer: "John Doe" (ID: C099, City: Mumbai)
Product: "Gaming Laptop" (ID: P555, Category: Electronics)
Line Item: 
  - Quantity: 2
  - Unit Price: ₹50,000
  - Discount: ₹5,000
```

---

### 2. Data Warehouse Transformation (OLAP)

#### Step A: Dimension Lookup & Creation

The ETL process maps the raw entities to their corresponding Dimensions.

**dim_date:** The date "2024-01-15" is looked up to find its corresponding key.

```json
{
  "date_key": 20240115,
  "full_date": "2024-01-15",
  "day_of_week": "Monday",
  "day_num_of_month": 15,
  "month_num": 1,
  "month_name": "January",
  "quarter": "Q1",
  "year": 2024,
  "is_weekend": false
}
```

**dim_product:** The product "P555" is mapped to its current active record in the warehouse.

```json
{
  "product_key": 5,
  "product_id_natural": "P555",
  "product_name": "Gaming Laptop",
  "category": "Electronics",
  "subcategory": "Laptops",
  "current_price": 50000.00,
  "stock_status": "In Stock",
  "effective_start_date": "2023-11-01",
  "effective_end_date": null,
  "is_current": true
}
```

**dim_customer:** The customer "C099" is mapped to their warehouse record.

```json
{
  "customer_key": 12,
  "customer_id_natural": "C099",
  "full_name": "John Doe",
  "email": "john.doe@email.com",
  "city": "Mumbai",
  "state": "Maharashtra",
  "customer_segment": "VIP",
  "registration_date_key": 20230115
}
```

---

#### Step B: Fact Table Insertion

The numeric data is combined with the Dimension Keys to create the Fact record.

**fact_sales:**

```json
{
  "order_id": "101",
  "date_key": 20240115,
  "product_key": 5,
  "customer_key": 12,
  "quantity_sold": 2,
  "unit_price": 50000.00,
  "gross_amount": 100000.00,
  "discount_amount": 5000.00,
  "net_amount": 95000.00
}
```

**Calculation Verification:**
- `gross_amount` = `quantity_sold * unit_price` = 2 × 50,000 = 100,000
- `net_amount` = `gross_amount - discount_amount` = 100,000 - 5,000 = 95,000

---

### 3. Query Example: Business Intelligence Report

**Business Question:** "What was the total revenue by product category in Q1 2024?"

**SQL Query:**
```sql
SELECT 
    dp.category,
    SUM(fs.net_amount) AS total_revenue,
    SUM(fs.quantity_sold) AS total_units_sold
FROM 
    fact_sales fs
    INNER JOIN dim_date dd ON fs.date_key = dd.date_key
    INNER JOIN dim_product dp ON fs.product_key = dp.product_key
WHERE 
    dd.quarter = 'Q1' 
    AND dd.year = 2024
    AND dp.is_current = true
GROUP BY 
    dp.category
ORDER BY 
    total_revenue DESC;
```

**Result:**
| Category | Total Revenue | Total Units Sold |
|----------|---------------|------------------|
| Electronics | ₹2,500,000 | 50 |
| Fashion | ₹150,000 | 200 |

---

## Summary

This Star Schema design provides:

✅ **Atomic-level granularity** for maximum analytical flexibility  
✅ **Surrogate keys** for performance and historical accuracy  
✅ **SCD Type 2** product tracking to preserve historical context  
✅ **Hierarchical dimensions** supporting drill-down and roll-up operations  
✅ **Optimized structure** for fast aggregation and reporting  

The schema is designed to support complex business intelligence queries while maintaining data integrity and query performance at scale.
