import sqlite3
import os

DB_PATH = "nutricart_vault.db"

def init_db():
    """Initializes the SQLite database and creates the feedback table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table to store persistent user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feedback (
            thread_id TEXT,
            product_name TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (thread_id, product_name)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def save_dislike(thread_id: str, product: str):
    """Saves a blacklisted product to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_feedback (thread_id, product_name, action)
        VALUES (?, ?, 'dislike')
    ''', (thread_id, product))
    conn.commit()
    conn.close()

def get_dislikes(thread_id: str):
    """Retrieves all blacklisted products for a specific thread."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT product_name FROM user_feedback WHERE thread_id = ? AND action = "dislike"', (thread_id,))
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results