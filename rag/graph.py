import logging
import re
from typing import TypedDict, List, Any, Optional, Literal, Annotated, Sequence
from datetime import datetime, timedelta

import weaviate
from weaviate.classes.query import Filter
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.rag import config
from src.rag.parser import extract_normalized_filters
from src.utils.init_db import get_dislikes  # Restoring your historical vault lookup

# -----------------------------
# 1. UPGRADED STATE SPACE
# -----------------------------
class MultiAgentState(TypedDict):
    # Core multi-agent message trace (appends automatically via add_messages)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str  # Tracks execution targets: "Intake" | "Inventory" | "Aggregate" | "FINISH"
    
    # State data slots retained from your original project
    question: str
    filters: dict
    results: List[dict[str, Any]]
    answer: str
    customer_id: str
    mode: str 
    time_frame: Optional[Literal["weekly", "monthly", "yearly"]]
    safety_status: str 
    customer_contact: dict 
    is_approved: bool

# -----------------------------
# 2. THE SUPERVISOR AGENT
# -----------------------------
class RouteDecision(BaseModel):
    next: Literal["Intake", "Inventory", "Aggregate", "FINISH"]

def supervisor_agent(state: MultiAgentState) -> dict:
    """Orchestrates runtime routing decisions by looking at message trajectories."""
    system_instruction = (
        "You are the Director of NutriCart Intelligence.\n"
        "Analyze the message history and decide which agent or step must execute next:\n"
        "- 'Intake': If safety filtering, intent mapping, or SQLite user preference lookup hasn't happened yet.\n"
        "- 'Inventory': When filters are ready and you need to query the Weaviate vector database for products.\n"
        "- 'Aggregate': If product results are available AND mode is 'consumption', to run the math loop.\n"
        "- 'FINISH': When the structural answers/reports are generated and ready to leave the team graph."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("placeholder", "{messages}")
    ])
    
    # Forcing structured output tracking onto your local Ollama runtime
    llm = ChatOllama(model="llama3.2:3b").with_structured_output(RouteDecision)
    decision_chain = prompt | llm
    
    response = decision_chain.invoke({"messages": state["messages"]})
    return {"next": response.next}

# -----------------------------
# 3. DOMAIN WORKER AGENTS & NODES
# -----------------------------

@traceable(name="Intake_Agent")
async def intake_agent(state: MultiAgentState) -> dict:
    """Handles inputs, extracts filters, and pulls long-term dislikes from SQLite."""
    # Retaining your exact parsing logic
    question = state["messages"][0].content.lower() 
    filters = await extract_normalized_filters(question) or {}

    # Retaining your exact mode detection rules
    if any(w in question for w in ["how much", "total", "summary", "consumed", "eaten"]):
        mode = "consumption"
    elif any(w in question for w in ["compare", "vs"]):
        mode = "comparison"
    else:
        mode = "discovery"

    # Retaining your time frame detection
    time_frame = None
    if mode == "consumption":
        time_frame = "weekly"
        if "week" in question: time_frame = "weekly"
        elif "month" in question: time_frame = "monthly"
        elif "year" in question: time_frame = "yearly"

    # Retaining your customer ID padding regex normalization
    c_id_raw = state.get("customer_id") or filters.get("customer_id", "C001")
    customer_id = f"C{int(re.sub(r'\D', '', str(c_id_raw)) or 1):03d}"
    
    # --- Restoring Persistent Memory Connection ---
    # Hydrating the state context using your local SQLite vault helper
    dislikes = get_dislikes(customer_id)
    filters["disliked_products"] = dislikes
    
    log_text = f"[Intake Complete] Mode: {mode}, User: {customer_id}, Excluded Items: {dislikes}"
    
    return {
        "filters": filters, 
        "customer_id": customer_id, 
        "mode": mode, 
        "time_frame": time_frame,
        "messages": [AIMessage(content=log_text, name="IntakeAgent")]
    }

@traceable(name="Inventory_Agent")
async def inventory_agent(state: MultiAgentState) -> dict:
    """Dedicated exclusively to vector indexing search policies against Weaviate."""
    try:
        with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
            collection = client.collections.get(config.COLLECTION_NAME)
            filter_clauses = []

            # 1. Date/User Filter Processing
            if state["mode"] == "consumption" and state["time_frame"]:
                filter_clauses.append(Filter.by_property("customer_id").equal(state["customer_id"]))

            # 2. Injecting Long-Term SQLite Blacklist into Weaviate Hardware Filtering
            blacklist = state.get("filters", {}).get("disliked_products", [])
            for item in blacklist:
                filter_clauses.append(Filter.by_property("product_name").not_equal(item))

            # Execute Hybrid Vector Search
            response = collection.query.hybrid(
                query=state["messages"][0].content,
                filters=Filter.all_of(filter_clauses) if filter_clauses else None,
                limit=50,
                return_properties=["product_name", "added_sugar", "protein", "calories"]
            )
            
            matched_items = [obj.properties for obj in response.objects]
            log_text = f"[Inventory Search Complete] Retrieved {len(matched_items)} records."
            
            return {
                "results": matched_items,
                "messages": [AIMessage(content=log_text, name="InventoryAgent")]
            }
    except Exception as e:
        return {
            "results": [], 
            "messages": [AIMessage(content=f"Search failed: {str(e)}", name="InventoryAgent")]
        }

@traceable(name="Nutrition_Aggregation")
async def aggregation_node(state: MultiAgentState) -> dict:
    """Pure computing node for calculations (unchanged, fast deterministic math loop)."""
    results = state.get("results", [])
    time_label = state.get("time_frame", "period").capitalize()
    
    if not results:
        report = f"I couldn't find any consumption logs for your {time_label} report."
        return {"answer": report, "messages": [AIMessage(content=report)]}

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
    return {"answer": report, "messages": [AIMessage(content="Report Aggregated.")]}

# -----------------------------
# 4. UPDATED MULTI-AGENT GRAPH COMPILATION
# -----------------------------
workflow = StateGraph(MultiAgentState)

# Register the agents and nodes
workflow.add_node("Supervisor", supervisor_agent)
workflow.add_node("Intake", intake_agent)
workflow.add_node("Inventory", inventory_agent)
workflow.add_node("Aggregate", aggregation_node)
workflow.add_node("Generate", generate_node) # Connects your existing copywriting node

# Worker nodes always route their state additions back to the Supervisor
workflow.add_edge("Intake", "Supervisor")
workflow.add_edge("Inventory", "Supervisor")
workflow.add_edge("Aggregate", "Supervisor")
workflow.add_edge("Generate", "Supervisor")

# Dynamic execution path resolution evaluated by the Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next"],
    {
        "Intake": "Intake",
        "Inventory": "Inventory",
        "Aggregate": "Aggregate",
        "Generate": "Generate",
        "FINISH": END # Exits the core agent loop smoothly to finalize output
    }
)

workflow.add_edge(START, "Supervisor")
app_graph = workflow.compile()