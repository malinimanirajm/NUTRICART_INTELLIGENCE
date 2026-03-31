import os
import re
import json
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

class NutritionFilters(BaseModel):
    customer_id: Optional[str] = Field(None)
    min_protein: Optional[float] = Field(None)
    max_sugar: Optional[float] = Field(None)
    max_calories: Optional[float] = Field(None)
    category: Optional[str] = Field(None)


# -----------------------------
# LLMs
# -----------------------------
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
structured_llm = gemini_llm.with_structured_output(NutritionFilters)
ollama_llm = ChatOllama(model="llama3.2:3b", temperature=0)


async def extract_normalized_filters(question: str) -> dict:
    # Try Gemini
    try:
        result = await structured_llm.ainvoke(question)
        if result:
            return {k: v for k, v in result.model_dump().items() if v is not None}
    except Exception as e:
        print("Gemini failed:", e)

    # Fallback Ollama
    prompt = f"""
    Extract filters as JSON.

    Rules:
    - max_sugar: number only
    - min_protein: number only
    - max_calories: number only
    - customer_id: format C001

    Query: {question}
    """
    try:
        response = await ollama_llm.ainvoke(prompt)
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            filters = {}
            if "customer_id" in data:
                num = int(re.sub(r"\D", "", str(data["customer_id"])))
                filters["customer_id"] = f"C{num:03d}"
            if "max_sugar" in data:
                filters["max_sugar"] = float(data["max_sugar"])
            if "min_protein" in data:
                filters["min_protein"] = float(data["min_protein"])
            if "max_calories" in data:
                filters["max_calories"] = float(data["max_calories"])
            if "category" in data:
                filters["category"] = str(data["category"]).lower()
            return filters
    except Exception as e:
        print("Ollama failed:", e)

    return {}