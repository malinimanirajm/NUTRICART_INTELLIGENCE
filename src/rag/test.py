import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthCheck")
load_dotenv()

def check_connections():
    logger.info("--- Starting NutriCart Health Check ---")
    
    # 2. Check Gemini Connection
    try:
        # Using the updated 2026 model string
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        response = llm.invoke("Say 'Gemini is Online'")
        logger.info(f"✅ Gemini Status: {response.content}")
    except Exception as e:
        logger.error(f"❌ Gemini Failed: {e}")

    # 3. Check LangSmith Connection
    try:
        client = Client()
        # Simply fetching project list to verify 403 status
        projects = list(client.list_projects())
        logger.info(f"✅ LangSmith Status: Connected. Found {len(projects)} projects.")
    except Exception as e:
        logger.error(f"❌ LangSmith Failed: {e}")

if __name__ == "__main__":
    check_connections()