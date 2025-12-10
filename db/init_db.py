"""
Database initialization script
Run this to create and seed the database
"""
import sqlite3
import os
from pathlib import Path

def init_database(db_path: str = "./db/library.db"):
    """Initialize the database with schema and seed data"""
    
    # Create db directory if it doesn't exist
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Connect to database (creates new file)
    print(f"Creating new database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema
    print("Creating tables...")
    with open("./db/schema.sql", "r") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    # Read and execute seed data
    print("Inserting seed data...")
    with open("./db/seed.sql", "r") as f:
        seed_sql = f.read()
        cursor.executescript(seed_sql)
    
    conn.commit()
    
    # Verify data
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    
    print(f"\n✅ Database initialized successfully!")
    print(f"   📚 Books: {book_count}")
    print(f"   👥 Customers: {customer_count}")
    print(f"   📦 Orders: {order_count}")
    
    conn.close()

if __name__ == "__main__":
    init_database()

