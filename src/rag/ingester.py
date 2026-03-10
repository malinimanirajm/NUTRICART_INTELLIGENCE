import weaviate
import weaviate.classes.config as wvc
import csv
import src.rag.config as config

def ingest_data():
    print("Connecting to Weaviate for ingestion...")
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    
    try:
        # 1. Clear old data
        if client.collections.exists(config.COLLECTION_NAME):
            client.collections.delete(config.COLLECTION_NAME)
            print("Deleted old Product collection")
        
        # --- Create collection with the correct v4 vector_config structure ---
        client.collections.create(
            name=config.COLLECTION_NAME,
            # FIX: We use Configure.Vectorizer.text2vec_transformers() 
            # as the value for the vectorizer_config parameter
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
            properties=[
                wvc.Property(name="product_name", data_type=wvc.DataType.TEXT),
                wvc.Property(name="product_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                wvc.Property(name="added_sugar", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="protein", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="calories", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="fat", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="fiber", data_type=wvc.DataType.NUMBER),
            ]
        )
        print("✅ Collection created")
        
        collection = client.collections.get(config.COLLECTION_NAME)

        # 3. Step One: Build the nutrition map first
        nutrition_map = {}
        with open(config.NUTRITION_FILE, "r") as nf:
            reader = csv.DictReader(nf)
            for row in reader:
                nutrition_map[row["product_id"]] = row

        # 3. Ingest and link
        print("Ingesting data...")
        with open(config.PRODUCTS_FILE, "r") as pf:
            reader = csv.DictReader(pf)
            for row in reader:
                nutri = nutrition_map.get(row["product_id"], {})
                
                # Helper to safely convert to float
                def to_float(val):
                    try: return float(val)
                    except: return 0.0

                p_val = to_float(nutri.get('protein_g'))
                s_val = to_float(nutri.get('added_sugar_g'))
                c_val = to_float(nutri.get('calories_100g'))
                f_val = to_float(nutri.get('fat_g'))
                fb_val = to_float(nutri.get('fiber_g'))

                # Create the text blob for RAG semantic search
                text_blob = (
                    f"Product: {row['product_name']}. "
                    f"Calories: {c_val}, Protein: {p_val}g, "
                    f"Sugar: {s_val}g, Fiber: {fb_val}g."
                )
                
                collection.data.insert(properties={
                    "product_name": row["product_name"],
                    "product_id": row["product_id"],
                    "text": text_blob,
                    "added_sugar": s_val,
                    "protein": p_val,
                    "calories": c_val,
                    "fat": f_val,
                    "fiber": fb_val
                })
        
        print("✅ Data ingested successfully.")
    finally:
        client.close()