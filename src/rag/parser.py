import os
import asyncio
import re
import json
from typing import Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class NutritionFilters(BaseModel):
    # Standardizing to customer_id to match your DB schema
    customer_id: Optional[str] = Field(None, description="The specific ID like C001 or C0009")
    min_protein: Optional[float] = Field(None, description="Minimum protein (g)")
    max_sugar: Optional[float] = Field(None, description="Maximum sugar (g)")
    # NEW: Added for Question 1 support
    max_calories: Optional[float] = Field(None, description="Maximum calories (kcal)")
    category: Optional[str] = Field(None, description="Food category like snacks, beverages, or dairy")

# 1. Initialize Gemini
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    max_retries=3
)
structured_gemini = gemini_llm.with_structured_output(NutritionFilters)

# 2. Local backup for Quota/Network failures
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def extract_normalized_filters(question: str) -> dict:
    """Extracts filters using Gemini, with a local Ollama fallback."""
    
    # --- Try Gemini First ---
    try:
        result = await structured_gemini.ainvoke(question)
        if result:
            # CHANGE: Ensure we return a clean dict, mapping user_id to customer_id if needed
            data = {k: v for k, v in result.model_dump().items() if v is not None}
            return data
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}. Trying Ollama...")

    # --- Fallback: Ollama + Explicit Prompt for User IDs ---
    ollama_prompt = (
        "TASK: Extract nutrition limits and user identity as JSON.\n"
        "RULES:\n"
        "- Extract 'user_id' if mentioned (e.g., 'user 101' -> '101').\n"
        "- Extract 'max_sugar' for sugar limits.\n"
        "- Extract 'min_protein' for protein requirements.\n"
        "- 'max_calories': Numeric limit for calories (e.g., 'less than 300' -> 300).\n"
        "- 'category': Extract food types (e.g., 'snacks', 'drinks').\n"
        f"USER QUERY: {question}\n"
        "JSON OUTPUT ONLY (keys: customer_id, max_sugar, min_protein, max_calories, category):"
    )
    
    try:
        response = await ollama_llm.ainvoke(ollama_prompt)
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            final_filters = {}

            c_id = data.get("customer_id") or data.get("user_id")
            if c_id:
                final_filters["customer_id"] = str(c_id).upper().replace("USER", "").strip()
            
            # Ensure proper types for the result
            if data.get("customer_id"):
                # Normalize customer_id to string and remove extra words like 'user'
                final_filters["customer_id"] = str(data["customer_id"]).replace("user", "").strip()
            if data.get("max_sugar") is not None:
                final_filters["max_sugar"] = float(data["max_sugar"])
            if data.get("min_protein") is not None:
                final_filters["min_protein"] = float(data["min_protein"])
            if data.get("category"):
                final_filters["category"] = str(data["category"]).lower()
                
            return final_filters
    except Exception as e:
        print(f"Ollama Extraction Error: {e}")
        
    return {}