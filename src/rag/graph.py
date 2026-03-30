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

# Internal imports - Fixed the config import
import src.rag.config as config
from src.rag.parser import extract_normalized_filters

# Setup Logging
logger = logging.getLogger(__name__)

# 1. Define State
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    comparison_results: List[dict[str, Any]]  # New: For "Trend" analysis
    answer: str
    aggregates: dict[str, Any]
    customer_id: str 
    time_delta: Optional[int]
    mode: str

# 2. Initialize LLM
backup_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def robust_llm_call(prompt: str) -> str:
    try:
        response = await backup_llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "I'm sorry, I encountered an error generating your nutrition report."

# 3. Nodes

@traceable(name="Node: Intent_Extraction")
async def extraction_node(state: AgentState):
    """Parses the question and normalizes IDs to C00X format."""
    filters = await extract_normalized_filters(state["question"])
    q = state["question"].lower()

    # 1. Mode Detection
    if any(word in q for word in ["compare", "versus", "vs", "more than", "change"]):
        mode = "comparison"
    elif any(word in q for word in ["consumed", "total", "ate", "my", "history"]):
        mode = "consumption"
    else:
        mode = "discovery"
    
    # 2. Identity Normalization (Ensuring C001, C002... 3-digit padding)
    c_id = filters.get("customer_id") or filters.get("user_id")
    if not c_id:
        match = re.search(r'C?0*(\d+)', q.upper()) 
        c_id = f"C{int(match.group(1)):03d}" if match else "Unknown Consumer"
    else:
        # Normalize whatever the parser found
        digits = re.sub(r"\D", "", str(c_id))
        c_id = f"C{int(digits):03d}"

    # 3. Time Window Logic
    days = 0
    if any(word in q for word in ["yearly", "year", "365"]): days = 365
    elif any(word in q for word in ["monthly", "month", "30"]): days = 30
    elif any(word in q for word in ["weekly", "week", "7"]): days = 7
    elif "yesterday" in q: days = 1
        
    return {"filters": filters, "customer_id": c_id, "time_delta": days, "mode": mode}

@traceable(name="Node: Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    """Queries Weaviate using context managers to prevent leaks."""
    # Using the URL from your config
    with weaviate.connect_to_local(host="127.0.0.1", port=8080) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        f = state.get("filters", {})
        mode = state.get("mode")
        c_id = state.get("customer_id")
        
        # Base Filter Logic
        weaviate_filter = None

        # 1. Identity filtering for Consumption/Comparison
        if mode in ["consumption", "comparison"]:
            weaviate_filter = Filter.by_property("customer_id").equal(c_id)
            
            if state.get("time_delta"):
                start_date = config.REFERENCE_DATE - timedelta(days=state["time_delta"])
                time_filt = Filter.by_property("date_consumed").greater_or_equal(start_date)
                weaviate_filter = (weaviate_filter & time_filt)
        
        # 2. Numeric Discovery Filters
        if f.get("max_sugar"):
            s_filt = Filter.by_property("added_sugar").less_than(float(f["max_sugar"]))
            weaviate_filter = (weaviate_filter & s_filt) if weaviate_filter else s_filt
        
        if f.get("min_protein"):
            p_filt = Filter.by_property("protein").greater_or_equal(float(f["min_protein"]))
            weaviate_filter = (weaviate_filter & p_filt) if weaviate_filter else p_filt

        # 3. Fetch primary results
        response = collection.query.near_text(
            query=state["question"],
            filters=weaviate_filter,
            limit=50,
            return_properties=["product_name", "added_sugar", "protein", "calories", "category", "date_consumed"]
        )
        
        primary_results = [obj.properties for obj in response.objects]

        # 4. Handle Comparison (Fetch the 'Previous' period)
        comp_results = []
        if mode == "comparison" and state.get("time_delta"):
            # If current is last 7 days, previous is 7 to 14 days ago
            end_prev = config.REFERENCE_DATE - timedelta(days=state["time_delta"])
            start_prev = end_prev - timedelta(days=state["time_delta"])
            
            comp_filter = Filter.by_property("customer_id").equal(c_id) & \
                          Filter.by_property("date_consumed").between(start_prev, end_prev)
            
            comp_resp = collection.query.fetch_objects(filters=comp_filter, limit=50)
            comp_results = [obj.properties for obj in comp_resp.objects]

        return {"results": primary_results, "comparison_results": comp_results}

@traceable(name="Node: Nutritional_Aggregation")
async def aggregation_node(state: AgentState):
    """Summarizes both primary and comparison data sets."""
    def summarize(items):
        summary = {}
        for item in items:
            cat = item.get("category") or "General"
            if cat not in summary:
                summary[cat] = {"calories": 0, "protein": 0, "sugar": 0, "count": 0}
            summary[cat]["calories"] += item.get("calories", 0)
            summary[cat]["protein"] += item.get("protein", 0)
            summary[cat]["sugar"] += item.get("added_sugar", 0)
            summary[cat]["count"] += 1
        return summary

    main_agg = summarize(state.get("results", []))
    comp_agg = summarize(state.get("comparison_results", []))

    return {"aggregates": {"current": main_agg, "previous": comp_agg}}

@traceable(name="Node: Answer_Synthesis")
async def generate_node(state: AgentState):
    mode = state.get("mode")
    agg = state.get("aggregates", {})
    
    if not state.get("results") and mode != "discovery":
        return {"answer": "I couldn't find any consumption records for that period in 2024."}

    if mode == "comparison":
        prompt = f"""
        Compare these two periods for user {state['customer_id']}:
        Current Period Totals: {agg['current']}
        Previous Period Totals: {agg['previous']}
        Task: Tell the user if their intake increased or decreased and highlight key changes.
        """
    elif mode == "consumption":
        total_kcal = sum(s['calories'] for s in agg['current'].values())
        prompt = f"Summarize this consumption for {state['customer_id']}: {agg['current']}. Total Kcal: {total_kcal}"
    else:
        items = "\n".join([f"- {r['product_name']}" for r in state['results'][:5]])
        prompt = f"The user is looking for products. Suggest these items: {items}"

    return {"answer": await robust_llm_call(prompt)}

# 4. Build Graph (Logic remains same, just uses the new nodes)
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

memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)