import logging
import re
from typing import TypedDict, List, Any, Optional
from datetime import datetime, timedelta, timezone

import weaviate
from weaviate.classes.query import Filter
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from langchain_ollama import ChatOllama

# Internal imports
from src.rag.parser import extract_normalized_filters

# Setup Logging
logger = logging.getLogger(__name__)

# 1. Define State
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    answer: str
    aggregates: dict[str, Any]
    customer_id: str  # Updated from user_id to match your DB schema
    time_delta: Optional[int]
    mode: str

# 2. Initialize LLM
backup_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def robust_llm_call(prompt: str) -> str:
    """Invokes Ollama with basic error handling."""
    try:
        response = await backup_llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "I'm sorry, I encountered an error generating your nutrition report."

# 3. Nodes

@traceable(name="Node: Intent_Extraction")
async def extraction_node(state: AgentState):
    """Parses the question for ID, nutrition limits, and time windows."""
    filters = await extract_normalized_filters(state["question"])
    q = state["question"].lower()

    # Mode Detection
    # If "consumed", "ate", "total", or "basis" is in the query, it's Question 2
    if any(word in q for word in ["consumed", "total", "basis", "ate", "my"]):
        mode = "consumption"
    else:
        mode = "discovery"
    
    # 1. Identity Logic (Matches your C001, C002... format)
    # Checks parser first, then falls back to regex
    c_id = filters.get("customer_id") or filters.get("user_id")
    if not c_id:
        match = re.search(r'C0*(\d+)', q.upper()) 
        c_id = f"C{int(match.group(1)):04d}" if match else "Unknown Consumer"
    
    # 2. Time Window Logic (Relative to the end of 2024)
    days = None
    if any(word in q for word in ["yearly", "year", "365"]):
        days = 365
    elif any(word in q for word in ["monthly", "month", "30"]):
        days = 30
    elif any(word in q for word in ["weekly", "week", "7"]):
        days = 7
    elif "yesterday" in q:
        days = 1
        
    return {"filters": filters, "customer_id": c_id, "time_delta": days,"mode": mode}

@traceable(name="Node: Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    """Queries Weaviate using the 2024 Reference Anchor."""
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    try:
        collection = client.collections.get("Product")
        f = state.get("filters", {})
        c_id = state.get("customer_id")
        days = state.get("time_delta")
        mode = state.get("mode")
        
        # --- THE 2024 ANCHOR ---
        # Since your data is from 2024, we treat Dec 31 as "Today"
        REFERENCE_DATE = datetime(2024, 12, 31, 23, 59, tzinfo=timezone.utc)
        
        # 1. Base Identity Filter
        weaviate_filter = None

        # QUESTION 2 LOGIC: Filter by Customer + Time
        if mode == "consumption":
            c_id = state.get("customer_id")
            weaviate_filter = Filter.by_property("customer_id").equal(c_id)
            
            if state.get("time_delta"):
                REF_DATE = datetime(2024, 12, 31, 23, 59, tzinfo=timezone.utc)
                start_date = REF_DATE - timedelta(days=state["time_delta"])
                time_filt = Filter.by_property("date_consumed").greater_or_equal(start_date)
                weaviate_filter = weaviate_filter & time_filt
        
        # 3. Numeric Filters (Protein/Sugar)
        if "max_sugar" in f:
            s_filt = Filter.by_property("added_sugar").less_than(float(f["max_sugar"]))
            weaviate_filter = (weaviate_filter & s_filt) if weaviate_filter else s_filt
        if "min_protein" in f:
            p_filt = Filter.by_property("protein").greater_or_equal(float(f["min_protein"]))
            weaviate_filter = (weaviate_filter & p_filt) if weaviate_filter else p_filt
        if "max_calories" in f: # Ensure your parser extracts this!
            c_filt = Filter.by_property("calories").less_than(float(f["max_calories"]))
            weaviate_filter = (weaviate_filter & c_filt) if weaviate_filter else c_filt

        # 4. Search Execution
        response = collection.query.near_text(
            query=state["question"],
            filters=weaviate_filter,
            limit=100,
            return_properties=["product_name", "added_sugar", "protein", "calories", "category", "date_consumed"]
        )
        
        return {"results": [obj.properties for obj in response.objects]}
    finally:
        client.close()

@traceable(name="Node: Nutritional_Aggregation")
async def aggregation_node(state: AgentState):
    """Sums nutrients and groups by your ingester categories."""
    results = state.get("results", [])
    summary = {}

    for item in results:
        cat = item.get("category") or "General Groceries"
        
        if cat not in summary:
            summary[cat] = {"calories": 0, "protein": 0, "sugar": 0, "count": 0}
        
        summary[cat]["calories"] += item.get("calories", 0)
        summary[cat]["protein"] += item.get("protein", 0)
        summary[cat]["sugar"] += item.get("added_sugar", 0)
        summary[cat]["count"] += 1

    return {"aggregates": summary}

@traceable(name="Node: Answer_Synthesis")
async def generate_node(state: AgentState):
    results = state.get("results", [])
    mode = state.get("mode")
    
    if not results:
        return {"answer": "No records found matching those criteria in 2024."}

    if mode == "discovery":
        # Question 1: List the products found
        items = "\n".join([f"- {r['product_name']}: {r['protein']}g Protein, {r['added_sugar']}g Sugar" for r in results[:5]])
        prompt = f"The user is looking for new products. Suggest these 5 items found in the database:\n{items}"
    else:
        # Question 2: Use the Aggregates
        agg = state.get("aggregates", {})
        total_kcal = sum(s['calories'] for s in agg.values())
        prompt = f"The user wants a consumption report for 2024. Total Calories: {total_kcal}. Breakdown: {agg}"

    return {"answer": await robust_llm_call(prompt)}

# 4. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("aggregate", aggregation_node)
workflow.add_node("generate", generate_node)

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "aggregate")
workflow.add_edge("aggregate", "generate")
workflow.add_edge("generate", END)

# 5. Compile
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)