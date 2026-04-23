import os
import re
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LLM Imports
from langchain_ollama import ChatOllama
# Keep Gemini import but we will use it sparingly
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# -----------------------------
# Pydantic Model
# -----------------------------
class NutritionFilters(BaseModel):
    customer_id: Optional[str] = Field(None, description="Format as C001")
    min_protein: Optional[float] = Field(None)
    max_sugar: Optional[float] = Field(None)
    max_calories: Optional[float] = Field(None)
    category: Optional[str] = Field(
        None, 
        description="One of: snack, dairy, pantry, bakery, beverages, produce"
    )
    granularity: Optional[str] = Field(
        None, 
        description="Time grouping: weekly, monthly, or yearly"
    )
    compare_current: Optional[str] = Field(None)
    compare_previous: Optional[str] = Field(None)

# -----------------------------
# LLM Initialization
# -----------------------------
# Ollama is now our primary for local-first reliability
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)

# Gemini is our secondary fallback
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

async def extract_normalized_filters(question: str) -> Dict[str, Any]:
    """
    Extracts structured filters from natural language.
    Prioritizes Local Ollama to avoid API Quota issues.
    """
    
    # 1. Primary Strategy: Local Ollama
    prompt = f"""
    You are a Nutrition AI Assistant. Extract nutrition filters from the user query into a JSON object.
    
    Rules:
    1. Dates: If a month is mentioned, use '2024-MM' (e.g., March is '2024-03').
    2. Comparison: Use 'compare_current' for the first date and 'compare_previous' for the second.
    3. Categories: snack, dairy, pantry, bakery, beverages, produce.
    4. Numeric: Extract min_protein, max_sugar, max_calories as numbers.
    
    STRICT: Return ONLY the JSON. No preamble.
    
    Query: "{question}"
    JSON Result:
    """

    try:
        response = await ollama_llm.ainvoke(prompt)
        # Cleaning the response (removing markdown or extra text)
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        match = re.search(r"(\{.*\})", clean_content, re.DOTALL)
        
        if match:
            data = json.loads(match.group(1))
            
            # Post-processing/Normalization
            filters = {}
            if data.get("customer_id"):
                num = "".join(filter(str.isdigit, str(data["customer_id"])))
                if num: filters["customer_id"] = f"C{int(num):03d}"
            
            # Carry over all other valid keys
            for key in ["min_protein", "max_sugar", "max_calories", "category", 
                        "granularity", "compare_current", "compare_previous"]:
                if data.get(key) is not None:
                    filters[key] = data[key]
            
            if filters:
                return filters
                
    except Exception as e:
        print(f"⚠️ Ollama extraction failed or timed out: {e}")

    # 2. Fallback: Gemini (Only if Local fails)
    # Note: We wrap this in a try block to catch the 429 errors safely
    try:
        # If you are debugging, you might want to uncomment this. 
        # For now, it's safer to stay local to avoid the quota crash.
        """
        structured_llm = gemini_llm.with_structured_output(NutritionFilters)
        result = await structured_llm.ainvoke(question)
        if result:
            return {k: v for k, v in result.model_dump().items() if v is not None}
        """
        pass
    except Exception as gem_e:
        print(f"❌ Gemini Fallback also failed (Quota?): {gem_e}")

    return {}