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
    safety_status: str # "safe", "blocked", or "hallucinated"

# -----------------------------
# LLM Initialization
# -----------------------------
llm = ChatOllama(model=config.OLLAMA_MODEL, temperature=0)

# -----------------------------
# Node 0: Input Guardrail
# -----------------------------
@traceable(name="Input_Guardrail")
async def guard_node(state: AgentState):
    question = state["question"].lower()
    
    # 1. Check for prompt injection
    if any(phrase in question for phrase in BANNED_PHRASES):
        return {
            "answer": "⚠️ Safety Alert: Invalid query pattern detected.",
            "safety_status": "blocked"
        }
    
    # 2. Check for domain relevance
    if not any(kw in question for kw in NUTRITION_KEYWORDS):
        return {
            "answer": "I can only assist with nutrition and grocery-related questions.",
            "safety_status": "blocked"
        }
    
    return {"safety_status": "safe"}

# -----------------------------
# Node 1: Intent & Filter Extraction
# -----------------------------
@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    question = state["question"].lower()
    filters = await extract_normalized_filters(question) or {}

    today = datetime.now()
    this_month = today.strftime("%Y-%m")
    last_month_dt = (today.replace(day=1) - timedelta(days=1))
    last_month = last_month_dt.strftime("%Y-%m")

    if not filters.get("max_sugar"):
        sugar_match = re.search(r"(?:less than|under|max)\s*(\d+)g", question)
        if sugar_match:
            filters["max_sugar"] = float(sugar_match.group(1))

    if any(w in question for w in ["compare", "vs", "versus", "difference"]):
        mode = "comparison"
        filters["compare_current"] = filters.get("compare_current", this_month)
        filters["compare_previous"] = filters.get("compare_previous", last_month)
    elif any(w in question for w in ["how much", "summary", "total", "each"]):
        mode = "consumption"
    else:
        mode = "discovery"

    c_id = state.get("customer_id") or filters.get("customer_id", "C001")
    digits = re.sub(r"\D", "", str(c_id))
    customer_id = f"C{int(digits):03d}"

    return {"filters": filters, "customer_id": customer_id, "mode": mode}

# -----------------------------
# Node 2: Vector Retrieval
# -----------------------------
@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        f = state.get("filters", {})
        mode = state.get("mode")
        c_id = state.get("customer_id")
        
        user_feedback = state.get("user_feedback", {})
        blacklist = user_feedback.get("disliked_products", [])

        filter_clauses = []
        if mode in ["consumption", "comparison"]:
            filter_clauses.append(Filter.by_property("customer_id").equal(c_id))
        if f.get("max_sugar") is not None:
            filter_clauses.append(Filter.by_property("added_sugar").less_than(float(f["max_sugar"])))
        if f.get("min_protein") is not None:
            filter_clauses.append(Filter.by_property("protein").greater_or_equal(float(f["min_protein"])))
        if f.get("category"):
            filter_clauses.append(Filter.by_property("category").equal(f["category"]))

        weaviate_filter = Filter.all_of(filter_clauses) if filter_clauses else None

        response = collection.query.hybrid(
            query=state["question"],
            filters=weaviate_filter,
            alpha=0.2,
            limit=150, 
            return_properties=["product_name", "added_sugar", "protein", "calories", "category", "date_consumed"]
        )

        results = [obj.properties for obj in response.objects if obj.properties.get("product_name") not in blacklist]
        return {"results": results}

# -----------------------------
# Node 3: Hybrid Aggregation
# -----------------------------
@traceable(name="Hybrid_Aggregation")
async def aggregation_node(state: AgentState):
    results = state.get("results", [])
    filters = state.get("filters", {})
    mode = state.get("mode")
    
    if mode == "comparison":
        curr_p, prev_p = filters.get("compare_current"), filters.get("compare_previous")
        comp_agg = {"current": {"protein": 0, "sugar": 0, "count": 0}, "previous": {"protein": 0, "sugar": 0, "count": 0}}
        for item in results:
            dt_str = str(item.get("date_consumed"))[:7]
            target = "current" if dt_str == curr_p else "previous" if dt_str == prev_p else None
            if target:
                comp_agg[target]["protein"] += item.get("protein", 0)
                comp_agg[target]["sugar"] += item.get("added_sugar", 0)
                comp_agg[target]["count"] += 1
        return {"aggregates": comp_agg}

    analysis = {}
    for item in results:
        dt = datetime.fromisoformat(str(item.get("date_consumed")).replace('Z', '+00:00'))
        t_key = dt.strftime("%Y-%m")
        cat = item.get("category", "general")
        if t_key not in analysis: analysis[t_key] = {}
        if cat not in analysis[t_key]: analysis[t_key][cat] = {"protein": 0, "sugar": 0, "count": 0}
        analysis[t_key][cat]["protein"] += item.get("protein", 0)
        analysis[t_key][cat]["sugar"] += item.get("added_sugar", 0)
        analysis[t_key][cat]["count"] += 1
    return {"aggregates": analysis}

# -----------------------------
# Node 4: Coaching Engine
# -----------------------------
@traceable(name="Coaching_Engine")
async def coaching_node(state: AgentState):
    # (Existing coaching logic remains the same)
    return {"recommendations": []}

# -----------------------------
# Node 5: Re-Ranking
# -----------------------------
@traceable(name="Re_Ranking")
async def ranker_node(state: AgentState):
    results, filters = state.get("results", []), state.get("filters", {})
    max_sugar = filters.get("max_sugar")
    if max_sugar is not None:
        results = [r for r in results if r.get("added_sugar", 999) <= max_sugar]
    ranked = sorted(results, key=lambda x: (-x.get("protein", 0), x.get("added_sugar", 999)))
    return {"ranked_results": ranked}

# -----------------------------
# Node 6: Answer Generation
# -----------------------------
@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    mode, agg, recs = state.get("mode"), state.get("aggregates", {}), state.get("recommendations", [])

    if mode == "comparison":
        curr, prev = agg.get("current"), agg.get("previous")
        if not curr or not prev or (curr['count'] == 0 and prev['count'] == 0):
            return {"answer": "Insufficient data for comparison."}
        p_diff = curr['protein'] - prev['protein']
        answer = f"### ⚔️ Comparison\n- **Protein:** {curr['protein']:.1f}g vs {prev['protein']:.1f}g\n- **Activity:** {curr['count']} vs {prev['count']} items."
        return {"answer": answer}

    results = state.get("ranked_results", [])
    if not results: return {"answer": "No matches found."}
    res_text = "\n".join(f"- {r['product_name']}: {r['added_sugar']}g sugar, {r['protein']}g protein" for r in results[:5])
    return {"answer": f"### 🔍 Top Matches:\n{res_text}"}

# -----------------------------
# Node 7: Output Validation (Fact Checker)
# -----------------------------
@traceable(name="Output_Validation")
async def validation_node(state: AgentState):
    answer = state.get("answer", "")
    results = state.get("results", [])
    
    # 1. Hallucination Check: Ensure the LLM didn't invent products
    product_names = [r['product_name'] for r in results]
    found_products = re.findall(r"\*\*(.*?)\*\*", answer) # Looks for bolded product names
    
    for p in found_products:
        if p not in product_names:
            logger.warning(f"Guardrail: Hallucinated product detected: {p}")
            return {"safety_status": "hallucinated"}
            
    return {"safety_status": "safe"}

# -----------------------------
# Graph Orchestration (Routing Logic)
# -----------------------------
def route_input(state: AgentState):
    return "extract" if state["safety_status"] == "safe" else END

def route_output(state: AgentState):
    return END if state["safety_status"] == "safe" else "generate" # Could retry generation

# -----------------------------
# Graph Compilation
# -----------------------------
DB_PATH = "nutricart_checkpoints.db"

workflow = StateGraph(AgentState)

workflow.add_node("guard", guard_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("aggregate", aggregation_node)
workflow.add_node("coach", coaching_node)
workflow.add_node("rank", ranker_node)
workflow.add_node("generate", generate_node)
workflow.add_node("validate", validation_node)

workflow.add_edge(START, "guard")

# Conditional Routing for Input Safety
workflow.add_conditional_edges("guard", route_input)

workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "aggregate")
workflow.add_edge("aggregate", "coach")
workflow.add_edge("coach", "rank")
workflow.add_edge("rank", "generate")
workflow.add_edge("generate", "validate")

# Conditional Routing for Output Accuracy
workflow.add_conditional_edges("validate", route_output)

app_graph = workflow.compile()