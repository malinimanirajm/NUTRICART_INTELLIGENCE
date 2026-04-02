import sqlite3
import os

DB_NAME = "nutricart_vault.db"

def fix_empty_vault():
    print(f"Checking {DB_NAME}...")
    
    # Connect (this creates the file if it doesn't exist, or opens it if it does)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # Create the table that was missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Optional: Add a 'preferences' table for future growth
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                customer_id TEXT PRIMARY KEY,
                dietary_goal TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Success: Tables created in nutricart_vault.db")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_empty_vault()