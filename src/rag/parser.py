import os
import re
import json
import logging
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LLM Imports
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
logger = logging.getLogger(__name__)

# -----------------------------
# Pydantic Model for Structure
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
    # NEW: Granularity for Analysis Mode
    granularity: Optional[Literal["weekly", "monthly", "yearly"]] = Field(
        None, 
        description="Time grouping for nutrition reports"
    )
    compare_current: Optional[str] = Field(None)
    compare_previous: Optional[str] = Field(None)

# -----------------------------
# LLM Initialization
# -----------------------------
# Primary: Local Ollama for speed and cost
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)

# Secondary: Gemini Fallback
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

async def extract_normalized_filters(question: str) -> Dict[str, Any]:
    """
    Extracts structured filters and time-based granularity from natural language.
    Handles Weekly/Monthly/Yearly analysis intent.
    """
    
    prompt = f"""
    You are a Nutrition Data Scientist. Parse the user's question into a JSON object.
    
    JSON Keys:
    - "customer_id": Extract ID (e.g., 'C001').
    - "granularity": Set to 'weekly', 'monthly', or 'yearly' IF they ask for a summary/total/report.
    - "min_protein", "max_sugar", "max_calories": Numeric values only.
    - "category": snack, dairy, pantry, bakery, beverages, produce.
    
    Rules:
    - If they ask "How much sugar did I eat this month?", granularity is "monthly".
    - If they ask "Show me my yearly protein", granularity is "yearly".
    - Return ONLY the JSON object. No conversation.
    
    Query: "{question}"
    JSON Result:
    """

    try:
        # 1. Attempt extraction with Local Ollama
        response = await ollama_llm.ainvoke(prompt)
        
        # Clean response string
        content = response.content.replace("```json", "").replace("```", "").strip()
        match = re.search(r"(\{.*\})", content, re.DOTALL)
        
        if match:
            data = json.loads(match.group(1))
            
            # Post-Extraction Normalization
            filters = {}
            
            # Normalize Customer ID (Ensure CXXX format)
            if data.get("customer_id"):
                num = "".join(filter(str.isdigit, str(data["customer_id"])))
                if num:
                    filters["customer_id"] = f"C{int(num):03d}"
            
            # Map valid fields to the output
            valid_keys = [
                "min_protein", "max_sugar", "max_calories", 
                "category", "granularity", "compare_current", "compare_previous"
            ]
            
            for key in valid_keys:
                if data.get(key) is not None:
                    # Specific check for granularity to match our Literal type
                    if key == "granularity":
                        val = str(data[key]).lower()
                        if val in ["weekly", "monthly", "yearly"]:
                            filters[key] = val
                    else:
                        filters[key] = data[key]
            
            return filters

    except Exception as e:
        logger.error(f"Ollama parsing failed: {e}")
        
        # 2. Fallback to Gemini if Ollama fails
        try:
            # Note: with_structured_output works best if you have a stable API connection
            structured_llm = gemini_llm.with_structured_output(NutritionFilters)
            result = await structured_llm.ainvoke(question)
            if result:
                return {k: v for k, v in result.model_dump().items() if v is not None}
        except Exception as gem_e:
            logger.error(f"Gemini fallback also failed: {gem_e}")

    return {}