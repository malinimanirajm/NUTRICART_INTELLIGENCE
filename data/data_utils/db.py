import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../data/sqlite/nutricart_vault.db"))

def get_db_connection():
    """Establishes an active connection thread with the SQLite vault."""
    return sqlite3.connect(DB_PATH)

def save_dislike(thread_id: str, customer_id: str, product_name: str):
    """Saves a blacklisted product to the user feedback table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_feedback (customer_id, product_name, feedback_type)
        VALUES (?, ?, 'dislike')
    ''', (customer_id, product_name))
    conn.commit()
    conn.close()

def get_dislikes(customer_id: str) -> list:
    """Retrieves all blacklisted products for a specific customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_name FROM user_feedback WHERE customer_id = ? AND feedback_type = 'dislike'",
        (customer_id,)
    )
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def calculate_historical_consumption(customer_id: str, days_back: int) -> dict:
    """Executes a pure arithmetic SQL aggregate query to fetch historical nutritional intake."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Mathematical aggregation over your transaction items and nutrition matrix
    query = """
        SELECT 
            SUM(n.calories_100g * (ti.quantity * 2)) as total_calories,
            SUM(n.protein_g * ti.quantity) as total_protein,
            SUM(n.added_sugar_g * ti.quantity) as total_sugar
        FROM transactions t
        JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
        JOIN nutrition n ON ti.product_id = n.product_id
        WHERE t.customer_id = ? 
          AND t.transaction_date >= date('2024-03-31', ?) -- Simulating relative to dataset end
    """
    
    cursor.execute(query, (customer_id, f"-{days_back} days"))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] is not None:
        return {"calories": row[0], "protein": row[1], "sugar": row[2]}
    return {"calories": 0, "protein": 0, "sugar": 0}