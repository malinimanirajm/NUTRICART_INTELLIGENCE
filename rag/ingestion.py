import weaviate
import weaviate.classes.config as config
import pandas as pd
import json
import os

def run_master_ingestion():
    # 1. Connect and Create Schema
    with weaviate.connect_to_local() as client:
        if client.collections.exists("NutricartUnified"):
            client.collections.delete("NutricartUnified")
            
        client.collections.create(
            name="NutricartUnified",
            vectorizer_config=config.Configure.Vectorizer.text2vec_ollama(
                api_endpoint="http://host.docker.internal:11434",
                model="nomic-embed-text"
            ),
            properties=[
                config.Property(name="content", data_type=config.DataType.TEXT),
                config.Property(name="data_type", data_type=config.DataType.TEXT),
                # Numeric fields for advanced filtering
                config.Property(name="protein_g", data_type=config.DataType.NUMBER),
                config.Property(name="added_sugar_g", data_type=config.DataType.NUMBER),
                config.Property(name="calories_100g", data_type=config.DataType.NUMBER),
                config.Property(name="carbs_g", data_type=config.DataType.NUMBER),
                config.Property(name="fat_g", data_type=config.DataType.NUMBER),
                config.Property(name="sodium_mg", data_type=config.DataType.NUMBER),
                config.Property(name="potassium_mg", data_type=config.DataType.NUMBER),
                # Categorical metadata
                config.Property(name="city", data_type=config.DataType.TEXT),
                config.Property(name="brand_name", data_type=config.DataType.TEXT),
                config.Property(name="category_name", data_type=config.DataType.TEXT)
            ]
        )
        
        collection = client.collections.get("NutricartUnified")
        print("Schema initialized. Starting ingestion...")

        # 2. Ingest PDF Knowledge
        with collection.batch.stream() as batch:
            if os.path.exists("final_chunks_preview.json"):
                with open("final_chunks_preview.json", "r") as f:
                    pdf_chunks = json.load(f)
                    for chunk in pdf_chunks:
                        batch.add_object(properties={
                            "content": chunk.get("summary_or_text", chunk["raw_content"]),
                            "data_type": "pdf_chunk"
                        })
            
            # 3. Join and Ingest CSV Data
            # Perform sequential joins
            df = pd.read_csv("data/raw/q1_2024_v1/transaction_items.csv") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/transactions.csv"), on="transaction_id") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/products.csv"), on="product_id") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/nutrition.csv"), on="product_id") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/customers.csv"), on="customer_id") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/brands.csv"), on="brand_id") \
                .merge(pd.read_csv("data/raw/q1_2024_v1/categories.csv"), on="category_id")

            for _, row in df.iterrows():
                summary = (f"Product {row['product_name']} from {row['brand_name']}. "
                           f"Purchased in {row['city']}. Category: {row['category_name']}. "
                           f"Nutrition: {row['protein_g']}g protein, {row['added_sugar_g']}g sugar.")
                
                batch.add_object(properties={
                    "content": summary,
                    "data_type": "transaction",
                    "protein_g": float(row['protein_g']),
                    "added_sugar_g": float(row['added_sugar_g']),
                    "calories_100g": float(row['calories_100g']),
                    "carbs_g": float(row['carbs_g']),
                    "fat_g": float(row['fat_g']),
                    "sodium_mg": float(row['sodium_mg']),
                    "potassium_mg": float(row['potassium_mg']),
                    "city": str(row['city']),
                    "category_name": str(row['category_name']),
                    "brand_name": str(row['brand_name'])
                })
    print("Master ingestion complete. Your data is unified and indexed.")

if __name__ == "__main__":
    run_master_ingestion()