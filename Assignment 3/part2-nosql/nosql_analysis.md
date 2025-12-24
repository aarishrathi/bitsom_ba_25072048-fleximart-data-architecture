# FlexiMart NoSQL Analysis: Transitioning to MongoDB

## Section A: Limitations of RDBMS
**Why our current relational database (SQL) struggles with diverse product data.**

1.  **The "Sparse Matrix" Problem (Attribute Variety):**
    Relational databases require a fixed schema. If we sell laptops and shoes in the same `products` table, we face a dilemma. We either create a massive table with columns for every possible attribute (`ram_size`, `shoe_size`, `fabric_type`, `cpu_speed`)—resulting in a table full of NULL values—or we create dozens of separate tables for each category. Both approaches are inefficient and slow to query.

2.  **Schema Rigidity (Evolution Pain):**
    Adding a new product type (e.g., "Smart Fridges" with unique attributes like `energy_rating` and `door_style`) requires an `ALTER TABLE` command. In a live production environment with millions of rows, altering the schema can lock the database, causing downtime. It makes the business slow to react to market trends.

3.  **Complexity of Nested Data (Reviews):**
    SQL forces us to normalize data. Storing customer reviews currently requires a separate `reviews` table joined by a foreign key. To display a single product page with its reviews, the database must perform an expensive JOIN operation every time. As traffic grows, these joins become a performance bottleneck.

---

## Section B: NoSQL Benefits
**How MongoDB solves these specific challenges.**

1.  **Flexible Schema (Polymorphism):**
    MongoDB is document-oriented (JSON-like). A single `products` collection can hold a document for a Laptop (with `ram`, `cpu` fields) right next to a document for a T-Shirt (with `size`, `color` fields). We do not need to define these fields in advance. We can simply insert the data as it comes. This eliminates the "Sparse Matrix" problem entirely.

2.  **Embedded Documents (Data Locality):**
    Instead of joining a separate `reviews` table, MongoDB allows us to embed reviews directly inside the product document as an array (e.g., `"reviews": [{ "user": "Alice", "rating": 5 }, ...]`). When we query for a product, we get its details *and* its reviews in a single, fast read operation. This significantly improves read performance for product pages.

3.  **Horizontal Scalability (Sharding):**
    As FlexiMart grows, a single SQL server will hit its vertical limit (CPU/RAM). MongoDB is designed to scale out (horizontally) using Sharding. It can automatically split our product catalog across multiple cheap servers. This allows us to handle infinite data growth without redesigning the architecture.

---

## Section C: Trade-offs
**The disadvantages of moving to MongoDB.**

1.  **Loss of ACID Transactions (Historically):**
    While modern MongoDB supports multi-document transactions, they are performance-heavy and not the default. SQL databases guarantee strict ACID compliance (Atomicity, Consistency, Isolation, Durability) for complex operations. If we need to update inventory and financial ledgers simultaneously, SQL offers safer, more robust guarantees against data corruption.

2.  **Join Complexity:**
    MongoDB is designed to avoid joins. If we need to perform complex analytics (e.g., "Show me sales trends by customer region joined with product manufacturer data"), MongoDB's aggregation framework is far more complex and often slower than a simple SQL JOIN. We sacrifice analytical power for operational speed.
