import os
import asyncio
import re
import json
from typing import Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama  # Ensure this is installed
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class NutritionFilters(BaseModel):
    min_protein: Optional[float] = Field(None, description="Minimum protein (g)")
    max_sugar: Optional[float] = Field(None, description="Maximum sugar (g)")

# 1. Initialize both models
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    max_retries=3
)
structured_gemini = gemini_llm.with_structured_output(NutritionFilters)

# Local backup for when Gemini is exhausted
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def extract_normalized_filters(question: str) -> dict:
    """Extracts filters using Gemini, with a local Ollama fallback on failure."""
    
    # --- Try Gemini First ---
    try:
        # We wrap the chain in a timeout to prevent hanging
        result = await structured_gemini.ainvoke(question)
        if result:
            return {k: v for k, v in result.model_dump().items() if v is not None}
    except Exception as e:
        # If it's a 429 (Quota) or other connection error, move to Ollama
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️ Gemini Quota Hit in Parser. Falling back to Local Ollama...")
        else:
            print(f"⚠️ Gemini encountered an error: {e}. Trying Ollama...")

    # --- Fallback: Ollama + Manual Extraction ---
    # Small models like Llama 3.2:3b need very explicit instructions
    # 2. Optimized Fallback for Ollama
    ollama_prompt = (
        "TASK: Extract nutrition limits as JSON.\n"
        "RULES:\n"
        "- Look for 'sugar' and 'protein'.\n"
        "- Use the exact keys: 'max_sugar' and 'min_protein'.\n"
        "- If the user says 'less than X sugar', set 'max_sugar' to X.\n"
        "- If the user says 'high protein', set 'min_protein' to 10 (default).\n"
        f"USER QUERY: {question}\n"
        "JSON OUTPUT ONLY:"
    )
    
    try:
        response = await ollama_llm.ainvoke(ollama_prompt)
        # Regex to find JSON block
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            # FORCE conversion to float and ensure keys exist
            final_filters = {}
            if data.get("max_sugar") is not None:
                final_filters["max_sugar"] = float(data["max_sugar"])
            if data.get("min_protein") is not None:
                final_filters["min_protein"] = float(data["min_protein"])
            return final_filters
    except Exception as e:
        print(f"Extraction Error: {e}")
    return {}
    
   