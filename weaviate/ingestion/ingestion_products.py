import csv
import os
from weaviate import connect_to_local

# =====================
# PATH SETUP
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../../data/raw/q1_2024_v1")
)

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")

COLLECTION_NAME = "Product"

# =====================
# CONNECT TO WEAVIATE
# =====================
client = connect_to_local(skip_init_checks=True)

try:
    # =====================
    # CREATE COLLECTION (DICT SCHEMA – STABLE)
    # =====================
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)

    client.collections.create_from_dict({
        "class": COLLECTION_NAME,
        "properties": [
            {"name": "product_id", "dataType": ["text"]},
            {"name": "product_name", "dataType": ["text"]},
            {"name": "category_id", "dataType": ["int"]},
            {"name": "brand_id", "dataType": ["int"]},
            {"name": "is_organic_available", "dataType": ["boolean"]},
            {"name": "text", "dataType": ["text"]},
        ],
        "vectorizer": "none"
    })

    collection = client.collections.get(COLLECTION_NAME)

    # =====================
    # LOAD NUTRITION DATA
    # =====================
    nutrition_map = {}

    with open(NUTRITION_FILE, "r") as nf:
        reader = csv.DictReader(nf)
        for row in reader:
            nutrition_map[row["product_id"]] = row

    # =====================
    # INGEST PRODUCTS
    # =====================
    with open(PRODUCTS_FILE, "r") as pf:
        reader = csv.DictReader(pf)

        for row in reader:
            nutrition = nutrition_map.get(row["product_id"], {})

            text_blob = (
                f"Product name: {row['product_name']}. "
                f"Category ID: {row['category_id']}. "
                f"Organic available: {row['is_organic_available']}. "
                f"Calories per 100g: {nutrition.get('calories_100g')}. "
                f"Protein: {nutrition.get('protein_g')} grams. "
                f"Fiber: {nutrition.get('fiber_g')} grams. "
                f"Added sugar: {nutrition.get('added_sugar_g')} grams."
            )

            collection.data.insert(
                properties={
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "category_id": int(row["category_id"]),
                    "brand_id": int(row["brand_id"]),
                    "is_organic_available": row["is_organic_available"] == "True",
                    "text": text_blob,
                }
            )

    print("✅ Product and nutrition data ingested successfully.")

finally:
    client.close()
