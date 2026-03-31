import os

# -----------------------------
# Base paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data/raw/q1_2024_v1")

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")

# -----------------------------
# Weaviate
# -----------------------------
WEAVIATE_HOST = "127.0.0.1"
WEAVIATE_PORT = 8080
COLLECTION_NAME = "Product"

# -----------------------------
# LLM
# -----------------------------
OLLAMA_MODEL = "llama3.2:3b"