import os

# -----------------------------
# Base paths
# -----------------------------
# Points to the root of NURICART_INTELLIGENCE
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data/raw/q1_2024_v1")

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition.csv")

# -----------------------------
# Databases (Vector & Relational)
# -----------------------------
WEAVIATE_HOST = "127.0.0.1"
WEAVIATE_PORT = 8080

# Collection for searching/comparing new products
PRODUCT_COLLECTION = "Product" 

# Collection for historical intake logs (Weekly/Monthly/Yearly reports)
LOGS_COLLECTION = "ConsumptionLog"

# Secure Vault for PII and user feedback
VAULT_DB_PATH = os.path.join(BASE_DIR, "nutricart_vault.db")

# -----------------------------
# LLM & AI Settings
# -----------------------------
OLLAMA_MODEL = "llama3.2:3b"
TEMPERATURE = 0

# -----------------------------
# Communication (Future-Proofing)
# -----------------------------
# Set these in your .env file
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886" # Twilio Sandbox