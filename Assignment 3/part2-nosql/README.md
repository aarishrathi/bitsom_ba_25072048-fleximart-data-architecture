# Part 2: NoSQL Analysis with MongoDB

## Overview

This section explores NoSQL database solutions, specifically MongoDB, to address limitations of relational databases when handling diverse product catalogs with varying attributes. The analysis includes theoretical discussion of RDBMS limitations, MongoDB benefits, and trade-offs, along with practical MongoDB operations.

## Files

- **nosql_analysis.md**: Comprehensive analysis comparing RDBMS limitations with NoSQL benefits
- **mongodb_operations.js**: MongoDB shell script demonstrating key operations
- **products_catalog.json**: Sample product catalog data in JSON format

## Setup

1. Ensure MongoDB is installed and running on your system

2. Load the product catalog data:
```bash
cd part2-nosql
mongoimport --db fleximart_catalog --collection products --file products_catalog.json --jsonArray
```

3. Run MongoDB operations:
```bash
mongosh < mongodb_operations.js
```

Or interactively:
```bash
mongosh
use fleximart_catalog
# Then copy/paste operations from mongodb_operations.js
```

## Operations Demonstrated

The `mongodb_operations.js` file includes:
1. **Data Loading**: Import JSON catalog into MongoDB collection
2. **Basic Queries**: Filter products by category and price
3. **Review Analysis**: Calculate average ratings using aggregation
4. **Complex Aggregation**: Advanced analytics queries

## Key Concepts

- **Flexible Schema**: MongoDB's document-oriented model eliminates the "sparse matrix" problem
- **Embedded Documents**: Related data (like reviews) can be stored within product documents
- **Horizontal Scalability**: MongoDB supports sharding for distributed data storage
- **Trade-offs**: Understanding when to use NoSQL vs SQL based on use case requirements

See `nosql_analysis.md` for detailed theoretical analysis.

