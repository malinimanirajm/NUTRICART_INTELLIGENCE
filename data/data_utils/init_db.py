import sqlite3
import os
import csv
import weaviate
import weaviate.classes.config as wvc

# Absolute path configurations mapped to the clean directory layout
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DB_DIR = os.path.join(PROJECT_ROOT, "data/sqlite")
DB_PATH = os.path.join(DB_DIR, "nutricart_vault.db")
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw/q1_2024_v1")

def init_sqlite():
    """Sets up core tables and seeds them with generated transactional history data."""
    os.makedirs(DB_DIR, exist_ok=True)
    print(f"Initializing SQLite Vault at: {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Internal Application Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL, -- 'like' or 'dislike'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                customer_id TEXT PRIMARY KEY,
                dietary_goal TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Operational Dataset Architecture Mappings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                city TEXT,
                state TEXT,
                household_size INTEGER,
                organic_preference TEXT,
                email TEXT,
                phone_number TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                category_id INTEGER,
                brand_id INTEGER,
                is_organic_available INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition (
                product_id TEXT PRIMARY KEY,
                calories_100g REAL,
                carbs_g REAL,
                fiber_g REAL,
                protein_g REAL,
                fat_g REAL,
                added_sugar_g REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT,
                transaction_date TEXT,
                transaction_time TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_items (
                item_id TEXT PRIMARY KEY,
                transaction_id TEXT,
                product_id TEXT,
                quantity INTEGER,
                is_organic_purchased INTEGER
            )
        """)
        conn.commit()

        # 3. Dynamic CSV Parsing and Database Seeding Block
        if os.path.exists(RAW_DATA_DIR):
            print("Found raw operational dataset. Beginning bulk migration loop...")
            
            # Seeding Customers
            with open(os.path.join(RAW_DATA_DIR, "customers.csv"), "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Enriching dataset entries with placeholder contact tokens for WhatsApp
                    cursor.execute("""
                        INSERT OR IGNORE INTO customers (customer_id, city, state, household_size, organic_preference, email, phone_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (row['customer_id'], row['city'], row['state'], row['household_size'], row['organic_preference'], f"{row['customer_id']}@example.com", "+1234567890"))
            
            # Seeding Products
            with open(os.path.join(RAW_DATA_DIR, "products.csv"), "r") as f:
                reader = csv.reader(f)
                next(reader) # Skip table header
                cursor.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", reader)

            # Seeding Nutrition
            with open(os.path.join(RAW_DATA_DIR, "nutrition.csv"), "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT OR IGNORE INTO nutrition (product_id, calories_100g, carbs_g, fiber_g, protein_g, fat_g, added_sugar_g)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (row['product_id'], row['calories_100g'], row['carbs_g'], row['fiber_g'], row['protein_g'], row['fat_g'], row['added_sugar_g']))

            # Seeding General Transactions
            with open(os.path.join(RAW_DATA_DIR, "transactions.csv"), "r") as f:
                reader = csv.reader(f)
                next(reader)
                cursor.executemany("INSERT OR IGNORE INTO transactions VALUES (?,?,?,?)", reader)

            # Seeding Granular Transaction Line Items
            with open(os.path.join(RAW_DATA_DIR, "transaction_items.csv"), "r") as f:
                reader = csv.reader(f)
                next(reader)
                cursor.executemany("INSERT OR IGNORE INTO transaction_items VALUES (?,?,?,?,?)", reader)

            conn.commit()
            print("Database migration completed successfully.")
        else:
            print("Warning: Raw data directory not located. Structural tables initialized without seed payloads.")

    except Exception as e:
        print(f"Error initializing SQLite database: {e}")
    finally:
        conn.close()


def init_weaviate():
    """Initializes local Weaviate schema collections matching agent graph filters."""
    print("Connecting to local Weaviate vector instance...")
    try:
        # Establish connection with the vector service
        with weaviate.connect_to_local(host="localhost", port=8080) as client:
            collection_name = "NutriCartProducts"
            
            # Drop the collection if it already exists to prevent duplicate indexes during development resets
            if client.collections.exists(collection_name):
                print(f"Collection '{collection_name}' already exists. Re-indexing...")
                client.collections.delete(collection_name)

            # Define schema collections matching filters in new_graph.py
            client.collections.create(
                name=collection_name,
                vectorizer_config=None,  # Handled locally via embedded tokens or manual models
                properties=[
                    wvc.Property(name="product_name", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="category_name", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="protein", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="added_sugar", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="calories", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="customer_id", data_type=wvc.DataType.TEXT),
                ]
            )
            print(f"Success: Weaviate collection '{collection_name}' initialized.")
    except Exception as e:
        print(f"Failed to initialize Weaviate server: {e}. Ensure docker container is running.")


def get_dislikes(customer_id: str) -> list:
    """Helper function utilized by Intake agent to fetch blacklist elements."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_name FROM user_feedback WHERE customer_id = ? AND feedback_type = 'dislike'",
            (customer_id,)
        )
        items = [row[0] for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        print(f"Could not fetch dislikes: {e}")
        return []


def fix_empty_vault():
    """Unified entry point running setup migrations."""
    init_sqlite()
    init_weaviate()


if __name__ == "__main__":
    fix_empty_vault()