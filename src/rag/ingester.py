import weaviate
import weaviate.classes.config as wvc
import csv
import random
import logging
from datetime import datetime, timedelta, timezone
from src.rag import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# NEW: Category Mapping Dictionary
# ---------------------------------------------------------
# This maps brand keywords and product types to clean categories
CATEGORY_MAPPING = {
    "snack": ["crunchy", "bite", "snack", "nest", "homebest", "treat"],
    "dairy": ["dairy", "milk", "yogurt", "cheese", "urban"],
    "pantry": ["staples", "valuemart", "pureharvest", "grain", "flour"],
    "bakery": ["bake", "bread", "pastry", "cake"],
    "beverages": ["drink", "sip", "water", "juice", "coolsip"],
    "produce": ["farm", "leaf", "fruit", "veg", "greenleaf"]
}

def get_category_from_name(name: str) -> str:
    name_lower = name.lower()
    for category, keywords in CATEGORY_MAPPING.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return "general"

# ---------------------------------------------------------
# Corrected safe_float (no upper bound restriction)
# ---------------------------------------------------------
def safe_float(val, default=0.0):
    try:
        f = float(val)
        if f < 0: 
            return default
        return f
    except:
        return default

def ingest_data():
    client = weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT)
    try:
        if client.collections.exists(config.COLLECTION_NAME):
            logger.info("Deleting existing collection to refresh data...")
            client.collections.delete(config.COLLECTION_NAME)

        logger.info("Creating collection with updated schema...")
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

        # Load Nutrition Map
        nutrition_map = {}
        with open(config.NUTRITION_FILE, "r") as nf:
            reader = csv.DictReader(nf)
            for row in reader:
                pid = row.get("product_id")
                if pid:
                    nutrition_map[pid] = row
        logger.info(f"Loaded nutrition data: {len(nutrition_map)} items")

        batch_size = 50
        objects_batch = []

        with open(config.PRODUCTS_FILE, "r") as pf:
            reader = csv.DictReader(pf)
            for i, row in enumerate(reader):
                product_id = row.get("product_id")
                product_name = row.get("product_name")
                if not product_id or not product_name:
                    continue

                nutri = nutrition_map.get(product_id, {})
                
                # Using the fixed safe_float
                sugar = safe_float(nutri.get("added_sugar_g"))
                protein = safe_float(nutri.get("protein_g"))
                calories = safe_float(nutri.get("calories_100g"))

                # Logic for dummy customer assignments
                user_num = (i // 5) + 1
                customer_id = f"C{user_num:03d}"

                # Dummy date logic
                start = datetime(2024, 1, 1, tzinfo=timezone.utc)
                consumption_date = start + timedelta(days=random.randint(0, 365))

                # Using the NEW mapping logic
                category = get_category_from_name(product_name)

                # Build descriptive blob for vector search
                text_blob = (
                    f"{product_name}. Category: {category}. "
                    f"Protein: {protein}g. Sugar: {sugar}g. Calories: {calories} kcal. "
                    f"Consumed by {customer_id} on {consumption_date.date()}."
                )

                obj = {
                    "product_name": product_name,
                    "product_id": product_id,
                    "customer_id": customer_id,
                    "category": category,
                    "date_consumed": consumption_date,
                    "text": text_blob,
                    "added_sugar": sugar,
                    "protein": protein,
                    "calories": calories
                }

                objects_batch.append(obj)
                if len(objects_batch) >= batch_size:
                    collection.data.insert_many(objects_batch)
                    objects_batch = []

            if objects_batch:
                collection.data.insert_many(objects_batch)

        logger.info("✅ Data ingestion complete with new Category Mapping and Calorie Fixes")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    ingest_data()