import weaviate
from db import get_db_connection

def seed_vector_inventory():
    print("Beginning Weaviate product vector ingestion...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pull products merged with their baseline nutritional attributes
    cursor.execute("""
        SELECT p.product_name, n.protein_g, n.added_sugar_g, n.calories_100g 
        FROM products p
        JOIN nutrition n ON p.product_id = n.product_id
    """)
    rows = cursor.fetchall()
    
    with weaviate.connect_to_local() as client:
        collection = client.collections.get("NutriCartProducts")
        
        # Batch insert to optimize background embedding execution
        with collection.batch.dynamic() as batch:
            for row in rows:
                batch.add_object(
                    properties={
                        "product_name": row[0],
                        "category_name": "Grocery",
                        "protein": float(row[1] or 0),
                        "added_sugar": float(row[2] or 0),
                        "calories": float(row[3] or 0)
                    }
                )
    print(f"Successfully vectorized and indexed {len(rows)} items into Weaviate.")
    conn.close()

if __name__ == "__main__":
    seed_vector_inventory()