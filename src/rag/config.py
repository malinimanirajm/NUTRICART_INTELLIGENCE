import os

# Paths (adjust based on your actual data location)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data/raw/q1_2024_v1")

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")

# Weaviate Settings (Fixed to use IP to avoid macOS DNS issues)
WEAVIATE_URL = "http://127.0.0.1:8080"
COLLECTION_NAME = "Product"

# LLM Settings
OLLAMA_MODEL = "llama3.2"