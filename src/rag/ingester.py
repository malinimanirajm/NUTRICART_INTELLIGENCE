import weaviate
import weaviate.classes.config as wvc
import csv
import src.rag.config as config
import random
from datetime import datetime, timedelta,timezone

def get_category_from_name(name: str) -> str:
    """Helper to auto-categorize items for portfolio visualization."""
    name = name.lower()
    if "dairy" in name: return "Dairy"
    if "staples" in name: return "Pantry Essentials"
    if "bake" in name: return "Bakery"
    if "sip" in name or "drink" in name: return "Beverages"
    if "farm" in name: return "Produce"
    return "General Groceries"

def ingest_data():
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    
    try:
        if client.collections.exists(config.COLLECTION_NAME):
            client.collections.delete(config.COLLECTION_NAME)
        
        # 3. SIMULATE 2024 TIME-SERIES DATA
        start_2024 = datetime(2024, 1, 1)
        # Randomly assign a date within the 366 days of 2024
        random_days = random.randint(0, 365)
        consumption_date = start_2024 + timedelta(days=random_days)
        # Ensure it is timezone aware if your retrieval uses UTC
        consumption_date = consumption_date.replace(tzinfo=timezone.utc)
        # FIX: Use vector_config (v4 standard)
        client.collections.create(
            name=config.COLLECTION_NAME,
            vector_config=wvc.Configure.Vectors.text2vec_transformers(), 
            properties=[
                wvc.Property(name="product_name", data_type=wvc.DataType.TEXT),
                wvc.Property(name="product_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="date_consumed", data_type=wvc.DataType.DATE),
                wvc.Property(name="customer_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                wvc.Property(name="added_sugar", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="protein", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="calories", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="category", data_type=wvc.DataType.TEXT), 
            ]
        )

        collection = client.collections.get(config.COLLECTION_NAME)

        # Build map and read products...
        # [Keep your nutrition_map logic here]

        # 1. Build the nutrition map first (Lookup Table)
        nutrition_map = {}
        with open(config.NUTRITION_FILE, "r") as nf:
            reader = csv.DictReader(nf)
            for row in reader:
                # We store the whole row using product_id as the key
                nutrition_map[row["product_id"]] = row

        with open(config.PRODUCTS_FILE, "r") as pf:
            reader = csv.DictReader(pf)
            for i,row in enumerate(reader):
                nutri = nutrition_map.get(row["product_id"], {})
                
                def to_float(val):
                    try: return float(val)  
                    except: return 0.0
                
                s_val = to_float(nutri.get('added_sugar_g'))
                p_val = to_float(nutri.get('protein_g'))
                c_val = to_float(nutri.get('calories_100g'))

                # 2. DYNAMIC INCREMENTAL USER ID
                # Every 5 rows belongs to a new user (C001, C002...)
                user_num = (i // 5) + 1
                assigned_user = f"C{user_num:03d}"

                # 3. SIMULATE TIME-SERIES DATA
                # Randomly assign a consumption date within the last 365 days
                days_ago = random.randint(0, 365)
                start_2024 = datetime(2024, 1, 1, tzinfo=timezone.utc)
                consumption_date = start_2024 + timedelta(days=random.randint(0, 365))
                
                cat = get_category_from_name(row['product_name'])

                text_blob = (
                    f"Consumer {assigned_user} consumed {row['product_name']} on {consumption_date.date()}. "
                    f"Category: {cat}. Protein: {p_val}g, Sugar: {s_val}g."
                )
                
                collection.data.insert(properties={
                    "product_name": str(row["product_name"]),
                    "product_id": str(row["product_id"]),
                    "customer_id": assigned_user,
                    "category": cat,
                    "date_consumed": consumption_date, # Stored
                    "text": text_blob,
                    "added_sugar": s_val, # Now stored as a number
                    "protein": p_val,
                    "calories": c_val
                })
        
        print("✅ Re-ingested: Data is now searchable by numeric filters.")
    finally:
        client.close()

if __name__ == "__main__":
    print("Starting data ingestion...")
    ingest_data()
    print("Done!")
    print("I am here")