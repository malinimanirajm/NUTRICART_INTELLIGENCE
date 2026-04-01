import os
import re
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

# -----------------------------
# Pydantic Model with Comparison Fields
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
    # SCENARIO 3: Period tracking
    compare_current: Optional[str] = Field(
        None, 
        description="The target/first period (Format: YYYY-MM)"
    )
    compare_previous: Optional[str] = Field(
        None, 
        description="The baseline/second period (Format: YYYY-MM)"
    )

# -----------------------------
# LLMs
# -----------------------------
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
# structured_output is very reliable with Gemini 2.0
structured_llm = gemini_llm.with_structured_output(NutritionFilters)
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def extract_normalized_filters(question: str) -> dict:
    # 1. Primary Extraction: Gemini
    try:
        system_prompt = (
            "You are a Nutrition AI Analyst. Categorize the user's request and extract fields.\n"
            "If it is a COMPARISON (e.g., 'X vs Y'), you MUST set:\n"
            "- compare_current: the FIRST date mentioned (Format: YYYY-MM)\n"
            "- compare_previous: the SECOND date mentioned (Format: YYYY-MM)\n\n"
            "If the user says 'March', use '2024-03'. If 'September', use '2024-09'."
        )
        
        result = await structured_llm.ainvoke([
            ("system", system_prompt),
            ("human", question)
        ])
        
        if result:
            return {k: v for k, v in result.model_dump().items() if v is not None}
    except Exception as e:
        print(f"Gemini Extraction failed: {e}")

    # 2. Fallback: Ollama with Hardened JSON Parsing
    prompt = f"""
    Extract nutrition filters as JSON. STRICTLY return ONLY the JSON block.
    
    Rules:
    - Comparison: 'compare_current' (1st date) and 'compare_previous' (2nd date) in YYYY-MM.
    - Categories: snack, dairy, pantry, bakery, beverages, produce.
    - Format: {{"customer_id": "C001", "compare_current": "YYYY-MM", "compare_previous": "YYYY-MM"}}

    Query: {question}
    """
    try:
        response = await ollama_llm.ainvoke(prompt)
        # Regex to find the first '{' and the last '}' to strip "Extra Data"
        match = re.search(r"(\{.*\})", response.content, re.DOTALL)
        if match:
            raw_json = match.group(1).strip()
            data = json.loads(raw_json)
            filters = {}
            
            # Normalization logic
            if data.get("customer_id"):
                num_match = re.search(r"\d+", str(data["customer_id"]))
                if num_match:
                    filters["customer_id"] = f"C{int(num_match.group()):03d}"
            
            # Transfer all valid fields
            valid_fields = [
                "max_sugar", "min_protein", "max_calories", "category", 
                "granularity", "compare_current", "compare_previous"
            ]
            for field in valid_fields:
                if data.get(field) is not None:
                    filters[field] = data[field]
                
            return {k: v for k, v in filters.items() if v is not None}
    except Exception as e:
        print(f"Ollama Fallback failed: {e}")

    return {}