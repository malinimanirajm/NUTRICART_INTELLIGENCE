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
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# -----------------------------
# Logging & Guardrail Constants
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BANNED_PHRASES = ["ignore previous", "system prompt", "developer mode", "jailbreak"]
NUTRITION_KEYWORDS = ["protein", "sugar", "eat", "snack", "buy", "calories", "compare", "food", "intake"]

# -----------------------------
# State Definition
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
    safety_status: str # "safe", "blocked", "hallucinated"
    customer_contact: dict  # {"email": "...", "phone": "..."}
    is_approved: bool

# -----------------------------
# LLM Initialization
# -----------------------------
llm = ChatOllama(model=config.OLLAMA_MODEL, temperature=0)

# -----------------------------
# NODES (Logic Units)
# -----------------------------

@traceable(name="Input_Guardrail")
async def guard_node(state: AgentState):
    """Node 0: Prevents prompt injections and off-topic queries."""
    question = state["question"].lower()
    if any(phrase in question for phrase in BANNED_PHRASES):
        return {"answer": "⚠️ Safety Alert: Invalid query pattern.", "safety_status": "blocked"}
    if not any(kw in question for kw in NUTRITION_KEYWORDS):
        return {"answer": "I only assist with nutrition/grocery queries.", "safety_status": "blocked"}
    return {"safety_status": "safe"}

@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    """Node 1: Parses natural language into structured filters."""
    question = state["question"].lower()
    filters = await extract_normalized_filters(question) or {}
    
    if any(w in question for w in ["compare", "vs"]): 
        mode = "comparison"
    elif any(w in question for w in ["how much", "total", "summary"]): 
        mode = "consumption"
    else: 
        mode = "discovery"

    # FIXED: Regex outside f-string to avoid SyntaxError
    c_id_raw = state.get("customer_id") or filters.get("customer_id", "C001")
    digits_only = re.sub(r'\D', '', str(c_id_raw))
    customer_id = f"C{int(digits_only or 1):03d}"
    
    return {"filters": filters, "customer_id": customer_id, "mode": mode}

@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    """Node 2: Fetches vector data and applies user blacklist."""
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        f = state.get("filters", {})
        blacklist = state.get("user_feedback", {}).get("disliked_products", [])

        filter_clauses = []
        if state["mode"] in ["consumption", "comparison"]:
            filter_clauses.append(Filter.by_property("customer_id").equal(state["customer_id"]))
        if f.get("max_sugar"):
            filter_clauses.append(Filter.by_property("added_sugar").less_than(float(f["max_sugar"])))

        response = collection.query.hybrid(
            query=state["question"],
            filters=Filter.all_of(filter_clauses) if filter_clauses else None,
            alpha=0.2,
            limit=50, 
            return_properties=["product_name", "added_sugar", "protein", "calories", "category"]
        )
        results = [obj.properties for obj in response.objects if obj.properties.get("product_name") not in blacklist]
        return {"results": results}

@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    """Node 3: Compiles the final response for the user."""
    results = state.get("results", [])
    if not results: return {"answer": "No matches found."}
    
    res_text = "\n".join(f"- **{r['product_name']}**: {r['added_sugar']}g sugar, {r['protein']}g protein" for r in results[:5])
    return {"answer": f"### 🔍 Top Nutrition Matches:\n{res_text}"}

@traceable(name="Output_Validation")
async def validation_node(state: AgentState):
    """Node 4: Fact-checks the output against retrieval results."""
    answer = state.get("answer", "")
    results = state.get("results", [])
    product_names = [r['product_name'] for r in results]
    found_products = re.findall(r"\*\*(.*?)\*\*", answer)
    
    for p in found_products:
        if p not in product_names:
            logger.warning(f"Hallucination detected: {p}")
            return {"safety_status": "hallucinated"}
    return {"safety_status": "safe"}

@traceable(name="Contact_Lookup")
async def lookup_contact_node(state: AgentState):
    """Node 5: Fetches customer contact info from the secure Vault."""
    c_id = state.get("customer_id")
    async with aiosqlite.connect("nutricart_vault.db") as db:
        async with db.execute(
            "SELECT email, phone_number FROM customers WHERE customer_id = ?", (c_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"customer_contact": {"email": row[0], "phone": row[1]}}
    return {"safety_status": "blocked", "answer": "Error: Contact details not found in Vault."}

@traceable(name="Outbound_Guard")
async def outbound_guard_node(state: AgentState):
    """Node 6: Final check before message is ready for external delivery."""
    answer = state.get("answer", "")
    banned = ["prescribe", "medication", "cure", "disease", "treat"]
    
    if any(word in answer.lower() for word in banned):
        return {"safety_status": "blocked", "answer": "⚠️ Content Blocked: Medical advice detected."}
    
    if state["customer_id"] in answer:
        answer = answer.replace(state["customer_id"], "Customer")

    return {"answer": answer, "safety_status": "safe"}

@traceable(name="Send_WhatsApp")
async def whatsapp_node(state: AgentState):
    """Node 7: Mock node to verify WhatsApp data delivery."""
    contact = state.get("customer_contact", {})
    phone = contact.get("phone")
    message = state.get("answer", "")

    if phone:
        print(f"\n--- 📲 WHATSAPP SIMULATION ---")
        print(f"TO: {phone}")
        print(f"BODY: {message}")
        print(f"-----------------------------\n")
    return {"is_approved": True}

# -----------------------------
# Routing Logic
# -----------------------------
def route_input(state: AgentState):
    return "extract" if state["safety_status"] == "safe" else END

def route_validation(state: AgentState):
    return "lookup_contact" if state["safety_status"] == "safe" else "generate"

def route_outbound(state: AgentState):
    return "send_whatsapp" if state["safety_status"] == "safe" else END

# -----------------------------
# Graph Compilation
# -----------------------------
workflow = StateGraph(AgentState)

workflow.add_node("guard", guard_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("generate", generate_node)
workflow.add_node("validate", validation_node)
workflow.add_node("lookup_contact", lookup_contact_node)
workflow.add_node("outbound_guard", outbound_guard_node)
workflow.add_node("send_whatsapp", whatsapp_node)

workflow.add_edge(START, "guard")
workflow.add_conditional_edges("guard", route_input)
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "validate")
workflow.add_conditional_edges("validate", route_validation)
workflow.add_edge("lookup_contact", "outbound_guard")
workflow.add_conditional_edges("outbound_guard", route_outbound)
workflow.add_edge("send_whatsapp", END)

app_graph = workflow.compile()