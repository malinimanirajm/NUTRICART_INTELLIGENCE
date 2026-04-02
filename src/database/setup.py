import sqlite3 # Standard library import
import os

# Use an absolute-ish path to be safe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DB_PATH = os.path.join(BASE_DIR, "../../nutricart_vault.db")

def fix_empty_vault():
    # Use a context manager (with) for cleaner code
    with sqlite3.connect(VAULT_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("✅ Vault Initialized.")