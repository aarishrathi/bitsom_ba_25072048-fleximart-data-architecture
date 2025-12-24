#!/bin/bash
# Script to execute warehouse schema and data files
# Usage: ./run_warehouse.sh [username] [password]

USERNAME=${1:-root}
PASSWORD=${2:-}

echo "Creating and populating FlexiMart Data Warehouse..."
echo "Using MySQL user: $USERNAME"

if [ -z "$PASSWORD" ]; then
    # Execute without password (will prompt)
    mysql -u "$USERNAME" -p < execute_warehouse.sql
else
    # Execute with password
    mysql -u "$USERNAME" -p"$PASSWORD" < execute_warehouse.sql
fi

if [ $? -eq 0 ]; then
    echo "✅ Warehouse created and populated successfully!"
    echo "You can now query the database with: mysql -u $USERNAME -p fleximart_dw"
else
    echo "❌ Error executing SQL files. Please check your MySQL credentials."
    echo "Alternative: Execute manually with:"
    echo "  mysql -u <username> -p < execute_warehouse.sql"
fi

