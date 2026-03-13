import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load here so the file is self-sufficient
load_dotenv()

# 2. Now the initialization will find the key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY") # Explicitly pass it to be safe
)

# 1. Define the Schema for Mathematical Filtering
class NutritionFilters(BaseModel):
    min_protein: Optional[float] = Field(None, description="Minimum protein in grams")
    max_sugar: Optional[float] = Field(None, description="Maximum sugar in grams")
    max_calories: Optional[float] = Field(None, description="Maximum calories (kcal)")
    max_sodium: Optional[float] = Field(None, description="Maximum sodium in GRAMS (1g = 1000mg)")

# 2. Initialize LLM with Structured Output
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
structured_llm = llm.with_structured_output(NutritionFilters)

# 3. The Normalization Prompt
SYSTEM_PROMPT = """
You are a precision nutritional data extractor for NutriCart.
STRICT UNIT RULES:
1. Normalize ALL weights to GRAMS (g). 
2. If the user mentions milligrams (mg), divide by 1000. 
   - Example: "500mg sodium" -> 0.5
   - Example: "2g sugar" -> 2.0
3. If no unit is mentioned, assume grams.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

async def extract_normalized_filters(question: str) -> dict:
    chain = prompt | structured_llm
    result = await chain.ainvoke({"question": question})
    # Filter out None values to keep the Weaviate query clean
    return {k: v for k, v in result.dict().items() if v is not None}