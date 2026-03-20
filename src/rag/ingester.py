import weaviate
import weaviate.classes.config as wvc
import csv
import src.rag.config as config

def ingest_data():
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    
    try:
        if client.collections.exists(config.COLLECTION_NAME):
            client.collections.delete(config.COLLECTION_NAME)
        
        # FIX: Use vector_config (v4 standard)
        client.collections.create(
            name="Product",
            vector_config=wvc.Configure.Vectors.text2vec_transformers(), 
            properties=[
                wvc.Property(name="product_name", data_type=wvc.DataType.TEXT),
                wvc.Property(name="product_id", data_type=wvc.DataType.TEXT),
                wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                wvc.Property(name="added_sugar", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="protein", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="calories", data_type=wvc.DataType.NUMBER),
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
            for row in reader:
                nutri = nutrition_map.get(row["product_id"], {})
                
                def to_float(val):
                    try: return float(val)  
                    except: return 0.0
                
                s_val = to_float(nutri.get('added_sugar_g'))
                p_val = to_float(nutri.get('protein_g'))
                c_val = to_float(nutri.get('calories_100g'))

                # FIX: text_blob must be a clean STRING (no commas at line ends)
                text_blob = (
                    f"Product: {row['product_name']}. "
                    f"Calories: {c_val}. "
                    f"Protein: {p_val}g, Sugar: {s_val}g."
                )
                
                collection.data.insert(properties={
                    "product_name": str(row["product_name"]),
                    "product_id": str(row["product_id"]),
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