import csv
import time
import weaviate
import weaviate.classes.config as wvc
import src.rag.config as config

def ingest_data():
    print("Connecting to Weaviate for ingestion...")
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    
    try:
        # Reset/Create Collection
        if client.collections.exists(config.COLLECTION_NAME):
            client.collections.delete(config.COLLECTION_NAME)
            print("Deleted old Product collection")
        
        # --- Create collection with vector config ---
        client.collections.create(
            name=config.COLLECTION_NAME,
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
            properties=[
                wvc.Property(name="product_name", data_type=wvc.DataType.TEXT),
                wvc.Property(name="product_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="text", data_type=wvc.DataType.TEXT),
            ]
        )
        print("✅ Collection created")
        
        collection = client.collections.get(config.COLLECTION_NAME)

        # --- LOAD NUTRITION DATA FIRST ---
        nutrition_map = {}
        with open(config.NUTRITION_FILE, "r") as nf:
            reader = csv.DictReader(nf)
            for row in reader:
                nutrition_map[row["product_id"]] = row

        # Ingest Data
        print("Ingesting data with nutritional details...")
        with open(config.PRODUCTS_FILE, "r") as pf:
            reader = csv.DictReader(pf)
            for row in reader:
                # --- GET NUTRITION INFO FOR THIS PRODUCT ---
                nutrition = nutrition_map.get(row["product_id"], {})
                
                # --- BUILD COMPREHENSIVE TEXT BLOB ---
                text_blob = (
                    f"Product name: {row['product_name']}. "
                    f"Category ID: {row['category_id']}. "
                    f"Calories per 100g: {nutrition.get('calories_100g', 'N/A')}. "
                    f"Protein: {nutrition.get('protein_g', 'N/A')} grams. "
                    f"Added sugar: {nutrition.get('added_sugar_g', 'N/A')} grams."
                )
                
                collection.data.insert(properties={
                    "product_name": row["product_name"],
                    "product_id": row["product_id"],
                    "text": text_blob
                })
        
        print("✅ Data ingested.")
    finally:
        client.close()