import logging
import re
from typing import TypedDict, List, Any, Optional
from datetime import datetime, timedelta

import weaviate
from weaviate.classes.query import Filter
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from langchain_ollama import ChatOllama
import aiosqlite

from src.rag import config
from src.rag.parser import extract_normalized_filters
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# -----------------------------
# Logging Setup
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Agent State Definition
# -----------------------------
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    ranked_results: List[dict[str, Any]]
    aggregates: dict[str, Any]
    recommendations: List[dict[str, Any]]
    answer: str
    customer_id: str
    mode: str
    user_feedback: dict

# -----------------------------
# LLM Initialization (Ollama)
# -----------------------------
# Using Ollama locally avoids the Gemini 429 Resource Exhausted errors.
llm = ChatOllama(model="llama3", temperature=0)

# -----------------------------
# Node 1: Intent & Filter Extraction
# -----------------------------
@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    question = state["question"].lower()
    # Extract entities using your custom parser
    filters = await extract_normalized_filters(question) or {}

    # Determine Scenario Mode
    if any(w in question for w in ["compare", "vs", "versus", "difference"]):
        mode = "comparison"
    elif any(w in question for w in ["how much", "summary", "total", "each"]):
        mode = "consumption"
    else:
        mode = "discovery"

    # Default customer ID logic
    c_id = state.get("customer_id") or "C001"
    
    return {
        "filters": filters,
        "customer_id": c_id,
        "mode": mode
    }

# -----------------------------
# Node 2: Vector Retrieval (Weaviate)
# -----------------------------
@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    # Connect to local Weaviate instance
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        
        user_feedback = state.get("user_feedback", {})
        blacklist = user_feedback.get("disliked_products", [])

        # Hybrid Search: Combines keyword matching with vector similarity
        response = collection.query.hybrid(
            query=state["question"],
            alpha=0.5,
            limit=15, 
            return_properties=[
                "product_name", "added_sugar", "protein", "calories", "category", "date_consumed"
            ]
        )

        # Apply blacklist filtering post-retrieval
        results = [
            obj.properties for obj in response.objects 
            if obj.properties.get("product_name") not in blacklist
        ]
        
        return {"results": results}

# -----------------------------
# Node 3: Ranking & Filtering
# -----------------------------
@traceable(name="Ranking_Logic")
async def ranker_node(state: AgentState):
    results = state.get("results", [])
    # Sort by protein descending, then sugar ascending
    ranked = sorted(
        results, 
        key=lambda x: (-x.get("protein", 0), x.get("added_sugar", 999))
    )
    return {"ranked_results": ranked}

# -----------------------------
# Node 4: Final Answer Generation
# -----------------------------
@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    results = state.get("ranked_results", [])
    if not results:
        return {"answer": "I'm sorry, I couldn't find any products that match your criteria."}
    
    # Format the top results into a readable list
    top_matches = "\n".join([
        f"- **{r['product_name']}**: {r['protein']}g protein, {r['added_sugar']}g sugar" 
        for r in results[:3]
    ])
    
    answer = f"### 🛒 NutriCart Insights\nBased on your query, here are the best matches:\n{top_matches}"
    return {"answer": answer}

# -----------------------------
# Graph Orchestration (The Workflow)
# -----------------------------
workflow = StateGraph(AgentState)

workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("rank", ranker_node)
workflow.add_node("generate", generate_node)

# Defining the flow sequence
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "rank")
workflow.add_edge("rank", "generate")
workflow.add_edge("generate", END)

# -----------------------------
# Async App Factory
# -----------------------------
DB_PATH = "nutricart_checkpoints.db"

async def get_app():
    """
    Factory function to initialize the SQLite connection and compile the graph.
    This ensures the checkpointer is created within the running async event loop.
    """
    conn = await aiosqlite.connect(DB_PATH)
    memory = AsyncSqliteSaver(conn)
    app = workflow.compile(checkpointer=memory)
    return app, conn