import sqlite3
import os

# This ensures the DB is always created in the project root, not inside src/utils/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../../nutricart_vault.db")

def fix_empty_vault():
    """Initializes the SQLite database and creates the feedback tables."""
    print(f"Checking Vault at: {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create the feedback table for likes/dislikes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL, -- 'like' or 'dislike'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create the preferences table for goals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                customer_id TEXT PRIMARY KEY,
                dietary_goal TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Success: NutriCart Vault is initialized.")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        conn.close()

def get_dislikes(customer_id: str) -> list:
    """Helper function to fetch all disliked products for a specific user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_name FROM user_feedback WHERE customer_id = ? AND feedback_type = 'dislike'",
            (customer_id,)
        )
        # Convert list of tuples [(item,)] to list of strings [item]
        items = [row[0] for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        print(f"⚠️ Could not fetch dislikes: {e}")
        return []

if __name__ == "__main__":
    # Allows you to run this file directly to test the setup
    fix_empty_vault()