/* 
   FLEXIMART MONGODB OPERATIONS
   Database: fleximart_catalog
   Collection: products
*/

// ============================================================================
// Operation 1: Load Data (1 mark)
// ============================================================================
// Import the provided JSON file into collection 'products'
//
// Command to run in terminal:
// mongoimport --db fleximart_catalog --collection products --file "products_catalog.json" --jsonArray
//
// Note: For a clean start, drop the collection first (uncomment if needed)
// db.products.drop();

use('fleximart_catalog'); // Switch to the database

print("Operation 1: Data loaded into 'products' collection");
print("Use: mongoimport --db fleximart_catalog --collection products --file 'products_catalog.json' --jsonArray");


// ============================================================================
// Operation 2: Basic Query (2 marks)
// ============================================================================
// Find all products in "Electronics" category with price less than 50000
// Return only: name, price, stock

print("\n--- Operation 2: Electronics under 50k ---");

db.products.find(
    { 
        category: "Electronics",
        price: { $lt: 50000 }
    },
    {
        _id: 0,
        name: 1,
        price: 1,
        stock: 1
    }
).forEach(printjson);


// ============================================================================
// Operation 3: Review Analysis (2 marks)
// ============================================================================
// Find all products that have average rating >= 4.0
// Use aggregation to calculate average from reviews array

print("\n--- Operation 3: Products with Avg Rating >= 4.0 ---");

db.products.aggregate([
    {
        $addFields: {
            // Calculate average of the 'rating' field inside the 'reviews' array
            avgRating: { $avg: "$reviews.rating" }
        }
    },
    {
        $match: {
            // Filter where calculated average is 4 or higher
            avgRating: { $gte: 4.0 }
        }
    },
    {
        $project: {
            product_id: 1,
            name: 1,
            category: 1,
            avgRating: { $round: ["$avgRating", 2] },
            _id: 0
        }
    }
]).forEach(printjson);


// ============================================================================
// Operation 4: Update Operation (2 marks)
// ============================================================================
// Add a new review to product "ELEC001"
// Review: {user: "U999", rating: 4, comment: "Good value", date: ISODate()}

print("\n--- Operation 4: Adding Review to ELEC001 ---");

db.products.updateOne(
    { product_id: "ELEC001" },
    {
        $push: {
            reviews: {
                user_id: "U999",
                username: "NewUser", // Adding username field to match schema
                rating: 4,
                comment: "Good value",
                date: new Date() // Uses current ISODate
            }
        }
    }
);

// Verify the update - show the last review added
printjson(db.products.findOne(
    { product_id: "ELEC001" },
    { reviews: { $slice: -1 }, name: 1, product_id: 1 }
));


// ============================================================================
// Operation 5: Complex Aggregation (3 marks)
// ============================================================================
// Calculate average price by category
// Return: category, avg_price, product_count
// Sort by avg_price descending

print("\n--- Operation 5: Average Price by Category ---");

db.products.aggregate([
    {
        $group: {
            _id: "$category", // Group by Category
            avg_price: { $avg: "$price" }, // Calculate average price
            product_count: { $sum: 1 } // Count products in this group
        }
    },
    {
        $sort: {
            avg_price: -1 // Sort Descending (Highest Price first)
        }
    },
    {
        $project: {
            category: "$_id", // Rename _id to category for readability
            avg_price: { $round: ["$avg_price", 2] }, // Round to 2 decimals
            product_count: 1,
            _id: 0
        }
    }
]).forEach(printjson);

print("\n=== All Operations Completed ===");

