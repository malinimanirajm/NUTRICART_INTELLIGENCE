import logging
import re
from typing import TypedDict, List, Any, Optional, Literal
from datetime import datetime, timedelta

import weaviate
from weaviate.classes.query import Filter
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from langchain_ollama import ChatOllama
import aiosqlite

from src.rag import config
from src.rag.parser import extract_normalized_filters

# -----------------------------
# State Definition
# -----------------------------
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    answer: str
    customer_id: str
    mode: str # "discovery", "consumption", or "comparison"
    time_frame: Optional[Literal["weekly", "monthly", "yearly"]]
    safety_status: str 
    customer_contact: dict 
    is_approved: bool

# -----------------------------
# NODES
# -----------------------------

@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    """Parses filters and detects if the user wants an analysis report."""
    question = state["question"].lower()
    filters = await extract_normalized_filters(question) or {}

    # Detect Mode
    if any(w in question for w in ["how much", "total", "summary", "consumed", "eaten"]):
        mode = "consumption"
    elif any(w in question for w in ["compare", "vs"]):
        mode = "comparison"
    else:
        mode = "discovery"

    # Detect Time Frame for Analysis
    time_frame = None
    if mode == "consumption":
        if "week" in question: time_frame = "weekly"
        elif "month" in question: time_frame = "monthly"
        elif "year" in question: time_frame = "yearly"
        else: time_frame = "weekly" # Default

    c_id_raw = state.get("customer_id") or filters.get("customer_id", "C001")
    customer_id = f"C{int(re.sub(r'\D', '', str(c_id_raw)) or 1):03d}"
    
    return {"filters": filters, "customer_id": customer_id, "mode": mode, "time_frame": time_frame}

@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    """Fetches data with date-based filtering for consumption analysis."""
    try:
        with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
            collection = client.collections.get(config.COLLECTION_NAME)
            filter_clauses = []

            # Date Filtering for Consumption Mode
            if state["mode"] == "consumption" and state["time_frame"]:
                days = {"weekly": 7, "monthly": 30, "yearly": 365}[state["time_frame"]]
                # Assuming your objects have a 'timestamp' property or using Weaviate internal metadata
                # For this example, we filter by the customer_id to get their history
                filter_clauses.append(Filter.by_property("customer_id").equal(state["customer_id"]))

            response = collection.query.hybrid(
                query=state["question"],
                filters=Filter.all_of(filter_clauses) if filter_clauses else None,
                limit=50,
                return_properties=["product_name", "added_sugar", "protein", "calories"]
            )
            return {"results": [obj.properties for obj in response.objects]}
    except Exception as e:
        return {"results": [], "safety_status": "blocked"}

@traceable(name="Nutrition_Aggregation")
async def aggregation_node(state: AgentState):
    """Computes totals for the Weekly/Monthly/Yearly report."""
    results = state.get("results", [])
    time_label = state.get("time_frame", "period").capitalize()
    
    if not results:
        return {"answer": f"I couldn't find any consumption logs for your {time_label} report."}

    total_protein = sum(float(r.get("protein", 0) or 0) for r in results)
    total_sugar = sum(float(r.get("added_sugar", 0) or 0) for r in results)
    total_calories = sum(float(r.get("calories", 0) or 0) for r in results)
    
    report = (
        f"📊 **{time_label} Nutrition Analysis**\n"
        f"Based on your logs, here is your intake:\n"
        f"- **Total Protein:** {total_protein:.1f}g\n"
        f"- **Total Sugar:** {total_sugar:.1f}g\n"
        f"- **Total Calories:** {total_calories:.0f} kcal\n"
        f"Keep up the great work!"
    )
    return {"answer": report}

# ... (Keep existing guard, lookup_contact, outbound_guard, and whatsapp nodes) ...

# -----------------------------
# Updated Routing Logic
# -----------------------------
def route_after_retrieval(state: AgentState):
    """Directs to Aggregation if in consumption mode, else to Generation."""
    if state["mode"] == "consumption":
        return "aggregate"
    return "generate"

# -----------------------------
# Updated Graph Compilation
# -----------------------------
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("guard", guard_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("generate", generate_node)
workflow.add_node("aggregate", aggregation_node) # NEW
workflow.add_node("validate", validation_node)
workflow.add_node("lookup_contact", lookup_contact_node)
workflow.add_node("outbound_guard", outbound_guard_node)
workflow.add_node("send_whatsapp", whatsapp_node)

# Define edges
workflow.add_edge(START, "guard")
workflow.add_conditional_edges("guard", route_input)
workflow.add_edge("extract", "retrieve")

# Conditional path after retrieval
workflow.add_conditional_edges("retrieve", route_after_retrieval, {
    "aggregate": "aggregate",
    "generate": "generate"
})

workflow.add_edge("aggregate", "validate")
workflow.add_edge("generate", "validate")

workflow.add_conditional_edges("validate", route_validation)
workflow.add_edge("lookup_contact", "outbound_guard")
workflow.add_conditional_edges("outbound_guard", route_outbound)
workflow.add_edge("send_whatsapp", END)

app_graph = workflow.compile()