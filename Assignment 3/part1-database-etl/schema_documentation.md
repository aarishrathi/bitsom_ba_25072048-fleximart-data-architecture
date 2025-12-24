# FlexiMart Database Schema Documentation

## Entity-Relationship Description (Text Format)

### ENTITY: customers
**Purpose:** Stores customer information and personal details for the FlexiMart e-commerce platform.

**Attributes:**
- `customer_id`: Unique identifier for each customer (Primary Key, Auto Increment)
- `first_name`: Customer's first name (Required, VARCHAR(50))
- `last_name`: Customer's last name (Required, VARCHAR(50))
- `email`: Customer's email address (Required, Unique, VARCHAR(100))
- `phone`: Customer's contact phone number (Optional, VARCHAR(20))
- `city`: City where the customer is located (Optional, VARCHAR(50))
- `registration_date`: Date when the customer registered with FlexiMart (Optional, DATE)

**Relationships:**
- One customer can place MANY orders (1:M relationship with orders table)

---

### ENTITY: products
**Purpose:** Stores product catalog information including pricing and inventory details.

**Attributes:**
- `product_id`: Unique identifier for each product (Primary Key, Auto Increment)
- `product_name`: Name of the product (Required, VARCHAR(100))
- `category`: Product category classification (Required, VARCHAR(50))
- `price`: Unit price of the product (Required, DECIMAL(10,2))
- `stock_quantity`: Current inventory level for the product (Optional, Default: 0, INT)

**Relationships:**
- One product can appear in MANY order items (1:M relationship with order_items table)

---

### ENTITY: orders
**Purpose:** Stores order transaction information linking customers to their purchases.

**Attributes:**
- `order_id`: Unique identifier for each order (Primary Key, Auto Increment)
- `customer_id`: Foreign key referencing the customer who placed the order (Required, INT)
- `order_date`: Date when the order was placed (Required, DATE)
- `total_amount`: Total monetary value of the order (Required, DECIMAL(10,2))
- `status`: Current status of the order (Optional, Default: 'Pending', VARCHAR(20))

**Relationships:**
- One order belongs to ONE customer (M:1 relationship with customers table)
- One order can contain MANY order items (1:M relationship with order_items table)

---

### ENTITY: order_items
**Purpose:** Stores individual line items within an order, representing specific products and quantities purchased.

**Attributes:**
- `order_item_id`: Unique identifier for each order line item (Primary Key, Auto Increment)
- `order_id`: Foreign key referencing the parent order (Required, INT)
- `product_id`: Foreign key referencing the product being ordered (Required, INT)
- `quantity`: Number of units of the product ordered (Required, INT)
- `unit_price`: Price per unit at the time of order (Required, DECIMAL(10,2))
- `subtotal`: Calculated total for this line item (quantity × unit_price) (Required, DECIMAL(10,2))

**Relationships:**
- One order item belongs to ONE order (M:1 relationship with orders table)
- One order item references ONE product (M:1 relationship with products table)

---

## Normalization Explanation

### 3NF Schema Explanation: FlexiMart Database

The FlexiMart schema achieves Third Normal Form (3NF) by rigorously organizing data to eliminate redundancy and dependency anomalies.

**1NF (Atomicity):** All tables (Customers, Products, Orders, Order Items) contain atomic values. Addresses are stored in a single city column (atomic for this scope), and there are no repeating groups (e.g., multiple products in one orders row).

**2NF (Partial Dependencies):**
Every non-key attribute must depend on the entire primary key.
Since all our tables use single-column Surrogate Primary Keys (e.g., `order_item_id` instead of a composite `order_id` + `product_id`), Partial Dependencies are impossible. Therefore, the schema automatically satisfies 2NF.

**3NF (Transitive Dependencies):** Non-key attributes depend only on the primary key, not on other non-key attributes.

Customer details (first_name, email) are in the customers table, referenced only by customer_id in orders. If they were in orders, email would depend on customer_id (a non-key attribute in that context), violating 3NF.

**Functional Dependencies:**
- Customers: customer_id → first_name, email, phone
- Products: product_id → product_name, price
- Orders: order_id → customer_id, order_date, total_amount
- Order_Items: order_item_id → order_id, product_id, quantity, subtotal

**Note on Derived Attributes:**
While `total_amount` in the orders table is functionally dependent on `order_id` for storage purposes, it is actually a **Derived Attribute** calculated as the sum of all `order_items.subtotal` values for that order. In strict 3NF theory, storing derived data is sometimes debated, but it is acceptable and commonly practiced for performance optimization (similar to Data Warehousing denormalization strategies). This allows quick access to order totals without aggregating order_items on every query.

**Anomalies Avoided:**
- **Update Anomaly:** Changing a customer's phone number happens in one place (customers table). Without normalization, you would have to update every single past order record for that customer, risking data inconsistency.
- **Insert Anomaly:** We can add a new product (e.g., "iPhone 16") to the products table immediately, even if no one has bought it yet. In an unnormalized system (e.g., a single "Sales" spreadsheet), you cannot list a product until a sale transaction exists.
- **Delete Anomaly:** If we delete an order, we strictly remove the transaction record. We do not lose the customer's data or the product's details, because those entities exist independently in their own parent tables.

---

## Sample Data Representation

### Table: customers

| customer_id | first_name | last_name | email                      | phone          | city      | registration_date |
|-------------|------------|-----------|----------------------------|----------------|-----------|-------------------|
| 1           | Rahul      | Sharma    | rahul.sharma@gmail.com     | 9876543210     | Bangalore | 2023-01-15        |
| 2           | Priya      | Patel     | priya.patel@yahoo.com      | +91-9988776655 | Mumbai    | 2023-02-20        |
| 3           | Amit       | Kumar     | amit.kumar@example.com     | 9765432109     | Delhi     | 2023-03-10        |

### Table: products

| product_id | product_name        | category    | price    | stock_quantity |
|------------|---------------------|-------------|----------|----------------|
| 1          | Samsung Galaxy S21  | Electronics | 45999.00 | 150            |
| 2          | Nike Running Shoes  | Fashion     | 3499.00  | 80             |
| 3          | Apple MacBook Pro   | Electronics | 129999.00| 45             |

### Table: orders

| order_id | customer_id | order_date | total_amount | status    |
|----------|-------------|------------|--------------|-----------|
| 1        | 1           | 2024-01-15 | 45999.00     | Completed |
| 2        | 2           | 2024-01-16 | 5998.00      | Completed |
| 3        | 3           | 2024-01-17 | 52999.00     | Pending   |

### Table: order_items

| order_item_id | order_id | product_id | quantity | unit_price | subtotal  |
|---------------|----------|------------|----------|------------|-----------|
| 1             | 1        | 1          | 1        | 45999.00   | 45999.00  |
| 2             | 2        | 2          | 2        | 2999.00    | 5998.00   |
| 3             | 3        | 3          | 1        | 52999.00   | 52999.00  |

