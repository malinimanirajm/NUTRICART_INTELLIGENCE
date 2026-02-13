"""
Full RAG Pipeline Setup Script (Weaviate v4.18+)
- Resets Product collection
- Re-ingests product + nutrition data
- Tests semantic search (nearText)
- Builds a sample RAG prompt
"""

import csv
import os
import time
import weaviate
from context_builder import retrieve_context  # your existing function
import ollama # <--- Import Ollama

# ===========================
# 0️⃣ Paths
# ===========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../data/raw/q1_2024_v1"))

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")
COLLECTION_NAME = "Product"

# ===========================
# 1️⃣ Connect to Weaviate safely
# ===========================
# Wait a few seconds if containers just started
print("Waiting 5 seconds for Weaviate + transformer to be ready...")
time.sleep(5)

client = weaviate.connect_to_local()
print("Connected to Weaviate ✅")

try:
    # ===========================
    # 2️⃣ Reset collection
    # ===========================
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
        print("Deleted old Product collection")

    client.collections.create_from_dict({
        "class": COLLECTION_NAME,
        "properties": [
            {"name": "product_id", "dataType": ["text"]},
            {"name": "product_name", "dataType": ["text"]},
            {"name": "category_id", "dataType": ["int"]},
            {"name": "brand_id", "dataType": ["int"]},
            {"name": "is_organic_available", "dataType": ["boolean"]},
            {"name": "text", "dataType": ["text"]}
        ],
        "vectorizer": "text2vec-transformers"
    })
    print("✅ Product collection created with vectorizer")

    # ===========================
    # 3️⃣ Load nutrition data
    # ===========================
    nutrition_map = {}
    with open(NUTRITION_FILE, "r") as nf:
        reader = csv.DictReader(nf)
        for row in reader:
            nutrition_map[row["product_id"]] = row

    # ===========================
    # 4️⃣ Ingest product data
    # ===========================
    collection = client.collections.get(COLLECTION_NAME)
    with open(PRODUCTS_FILE, "r") as pf:
        reader = csv.DictReader(pf)
        for row in reader:
            nutrition = nutrition_map.get(row["product_id"], {})
            text_blob = (
                f"Product name: {row['product_name']}. "
                f"Category ID: {row['category_id']}. "
                f"Organic available: {row['is_organic_available']}. "
                f"Calories per 100g: {nutrition.get('calories_100g', 'N/A')}. "
                f"Protein: {nutrition.get('protein_g', 'N/A')} grams. "
                f"Fiber: {nutrition.get('fiber_g', 'N/A')} grams. "
                f"Added sugar: {nutrition.get('added_sugar_g', 'N/A')} grams."
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

    print("✅ Products and nutrition data ingested successfully")

    # ===========================
    # 5️⃣ Test semantic search (nearText)
    # ===========================
    print("\nTesting semantic search (nearText)...")
    results = collection.query.near_text(
        query="high protein low sugar", # Passed as a string for nearText
        limit=5
    )

    # --- FIX STARTS HERE ---
    if results.objects:
        print("Top semantic matches:")
        for obj in results.objects:
            # Access properties directly from the object
            print("-", obj.properties.get("product_name"))
    else:
        print("No semantic matches found.")
    # --- FIX ENDS HERE ---


    # ===========================
# 6️⃣ Build RAG prompt and Get Answer
# ===========================

    question = "Which products are high in protein and low in sugar?"
    contexts = retrieve_context(question, top_k=5)

    if not contexts:
        contexts = ["No relevant context found."]

    context_block = "\n\n".join(contexts)

    prompt = f"""
    You are a nutrition intelligence assistant.

    Use the context below to answer the question accurately.
    If the answer is not in the context, say you don't know.

    Context:
    {context_block}

    Question:
    {question}

    Answer:
    """
    print("\nSample RAG Prompt:")
    print(prompt)

    # --- 💡 ADD THIS TO GET THE ANSWER FOR FREE 💡 ---
    print("\n--- Generating Answer (Local) ---")
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        print("Final Answer:")
        print(response['message']['content'])
    except Exception as e:
        print(f"Error calling Ollama: {e}")
# ------------------------------------------------

finally:
    # ===========================
    # 7️⃣ Close client
    # ===========================
    client.close()
    print("Connection to Weaviate closed ✅")
    # --- ADD THIS TO YOUR main.py ---


# ... your existing pipeline code ...

# Explicitly close the Ollama client socket to prevent ResourceWarning
if hasattr(ollama._client, '_client'):
    ollama._client._client.close()
