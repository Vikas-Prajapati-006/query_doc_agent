# test_agent.py
import sqlite3
import random
from datetime import datetime, timedelta
from src.pipeline.agent_pipeline import app_pipeline

# 1. Database Creation & Mega Data Seeding (1 Million Records Setup)
db_name = "database.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# SQLite configurations speed up karne ke liye
cursor.execute("PRAGMA synchronous = OFF;")
cursor.execute("PRAGMA journal_mode = MEMORY;")

print("=== Creating System Schema Tables ===")
# 1. Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
""")

# 2. Orders Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL
    );
""")

# 3. Products Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock_count INTEGER NOT NULL
    );
""")

# 4. Query Logs Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        execution_time_sec REAL NOT NULL,
        status TEXT NOT NULL
    );
""")

# --- B. BULK DATA GENERATOR MATRIX ---

cursor.execute("SELECT COUNT(*) FROM orders;")
if cursor.fetchone()[0] < 1000000:
    print("⏳ Seeding 1,000,000+ realistic rows into the database... Please wait a few seconds...")
    
    # 1. Products Populate karte hain pehle (Base inventory setup)
    cursor.execute("DELETE FROM products;")
    products_mock = [
        ('Mechanical Keyboard', 4500.0, 150),
        ('Wireless Mouse', 1200.0, 300),
        ('Gaming Monitor 4K', 28000.0, 45),
        ('RGB Mousepad', 800.0, 500),
        ('USB-C Hub Matrix', 2200.0, 120)
    ]
    cursor.executemany("INSERT INTO products (name, price, stock_count) VALUES (?, ?, ?);", products_mock)
    
    # 2. Users Populate (10,000 unique users matrix to distribute orders)
    cursor.execute("DELETE FROM users;")
    users_batch = []
    base_date = datetime(2026, 1, 1)
    for i in range(1, 10001):
        username = f"user_matrix_{i}"
        email = f"user_{i}@autonomous_node.com"
        created_at = (base_date + timedelta(days=random.randint(0, 100))).strftime('%Y-%m-%d')
        users_batch.append((username, email, created_at))
    cursor.executemany("INSERT INTO users (username, email, created_at) VALUES (?, ?, ?);", users_batch)

    # 3. Mega Orders Seeding (1,000,000 Rows Bulk Vector Injection)
    cursor.execute("DELETE FROM orders;")
    statuses = ['DELIVERED', 'PENDING', 'SHIPPED', 'CANCELLED']
    
    # Batch processing system taaki memory overload na ho
    batch_size = 100000
    total_rows = 1000000
    
    for start in range(0, total_rows, batch_size):
        orders_batch = []
        for _ in range(batch_size):
            user_id = random.randint(1, 10000)
            product_id = random.randint(1, 5)
            amount = round(random.uniform(500.0, 50000.0), 2)
            status = random.choice(statuses)
            orders_batch.append((user_id, product_id, amount, status))
        
        cursor.executemany("INSERT INTO orders (user_id, product_id, amount, status) VALUES (?, ?, ?, ?);", orders_batch)
        print(f"   Processed -> {start + batch_size} / {total_rows} rows injected.")

    # 4. Populating Query Logs
    cursor.execute("DELETE FROM query_logs;")
    cursor.execute("INSERT INTO query_logs (query_text, execution_time_sec, status) VALUES ('SELECT * FROM orders WHERE status = PENDING;', 4.82, 'SLOW');")

    conn.commit()
    print("🎯 Mega Scale Database Seeding Completed Successfully!")
else:
    print("✅ Database already populated with 1 Million+ entries. Skipping Seeding stage.")

conn.close()
print("=== Dummy Test DB Checked/Created with Full Scale Matrix ===")

# --- PIPELINE INGESTION BYPASS FOR PRODUCTION CONTAINER BOOT ---
# Niche ke test execution logic ko production mein load hone se bacha diya hai taaki RAM crash na ho.
#
# sample_initial_state = {
#     "raw_input": "Show me all records from the products table please"
# }
# test_config = {"configurable": {"thread_id": "db_agent_prod_session_01"}}
# print("=== Running LangGraph Pipeline Test ===")
# final_output_state = app_pipeline.invoke(sample_initial_state, config=test_config)
# print("\n=== Test Completed! Final Agent State Results: ===")
# print(f"Intent Vector Detected: {final_output_state.get('intent')}")
# print(f"Generated Vector Query: {final_output_state.get('generated_command')}")