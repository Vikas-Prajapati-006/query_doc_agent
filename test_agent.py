import sqlite3
import random
import os
from datetime import datetime, timedelta
from src.pipeline.agent_pipeline import app_pipeline


IS_RENDER = "RENDER" in os.environ

if IS_RENDER:
    TOTAL_ROWS = 2000
    USERS_COUNT = 500
    BATCH_SIZE = 1000
    print("🚀 [ENVIRONMENT]: Render Cloud Detected -> Dynamic Light Scaling Enabled (2,000 rows limit).")
else:
    TOTAL_ROWS = 1000000
    USERS_COUNT = 10000
    BATCH_SIZE = 100000
    print("💻 [ENVIRONMENT]: Local Machine Detected -> Full Scale Matrix Enabled (1,000,000 rows limit).")


db_name = "database.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()


cursor.execute("PRAGMA synchronous = OFF;")
cursor.execute("PRAGMA journal_mode = MEMORY;")

print("=== Creating System Schema Tables ===")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL
    );
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock_count INTEGER NOT NULL
    );
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        execution_time_sec REAL NOT NULL,
        status TEXT NOT NULL
    );
""")


cursor.execute("SELECT COUNT(*) FROM orders;")
current_count = cursor.fetchone()[0]

if current_count < TOTAL_ROWS:
    print(f"⏳ Seeding {TOTAL_ROWS:,}+ realistic rows into the database... Please wait a few seconds...")
    
   
    cursor.execute("DELETE FROM products;")
    products_mock = [
        ('Mechanical Keyboard', 4500.0, 150),
        ('Wireless Mouse', 1200.0, 300),
        ('Gaming Monitor 4K', 28000.0, 45),
        ('RGB Mousepad', 800.0, 500),
        ('USB-C Hub Matrix', 2200.0, 120)
    ]
    cursor.executemany("INSERT INTO products (name, price, stock_count) VALUES (?, ?, ?);", products_mock)
    
    
    cursor.execute("DELETE FROM users;")
    users_batch = []
    base_date = datetime(2026, 1, 1)
    for i in range(1, USERS_COUNT + 1):
        username = f"user_matrix_{i}"
        email = f"user_{i}@autonomous_node.com"
        created_at = (base_date + timedelta(days=random.randint(0, 100))).strftime('%Y-%m-%d')
        users_batch.append((username, email, created_at))
    cursor.executemany("INSERT INTO users (username, email, created_at) VALUES (?, ?, ?);", users_batch)

    
    cursor.execute("DELETE FROM orders;")
    statuses = ['DELIVERED', 'PENDING', 'SHIPPED', 'CANCELLED']
    
    for start in range(0, TOTAL_ROWS, BATCH_SIZE):
        orders_batch = []
        for _ in range(BATCH_SIZE):
            user_id = random.randint(1, USERS_COUNT)
            product_id = random.randint(1, 5)
            amount = round(random.uniform(500.0, 50000.0), 2)
            status = random.choice(statuses)
            orders_batch.append((user_id, product_id, amount, status))
        
        cursor.executemany("INSERT INTO orders (user_id, product_id, amount, status) VALUES (?, ?, ?, ?);", orders_batch)
        print(f"    Processed -> {start + BATCH_SIZE} / {TOTAL_ROWS} rows injected.")


    cursor.execute("DELETE FROM query_logs;")
    cursor.execute("INSERT INTO query_logs (query_text, execution_time_sec, status) VALUES ('SELECT * FROM orders WHERE status = PENDING;', 4.82, 'SLOW');")

    conn.commit()
    print("🎯 Database Seeding Completed Successfully!")
else:
    print(f"✅ Database already populated with {current_count:,}+ entries. Skipping Seeding stage.")

conn.close()
print("=== Dummy Test DB Checked/Created with Full Scale Matrix ===")