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
import sqlite3

from src.rag import config
from src.rag.parser import extract_normalized_filters
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

# -----------------------------
# LLM Initialization
# -----------------------------
llm = ChatOllama(model=config.OLLAMA_MODEL, temperature=0)

# -----------------------------
# Node 1: Intent & Filter Extraction
# -----------------------------
@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    question = state["question"].lower()
    filters = await extract_normalized_filters(question) or {}

    # --- FIX: Dynamic Date Calculation for Comparison ---
    # Ensures "this month" and "last month" work relative to today
    today = datetime.now()
    this_month = today.strftime("%Y-%m")
    last_month_dt = (today.replace(day=1) - timedelta(days=1))
    last_month = last_month_dt.strftime("%Y-%m")

    if not filters.get("max_sugar"):
        sugar_match = re.search(r"less than (\d+)g", question)
        if sugar_match:
            filters["max_sugar"] = float(sugar_match.group(1))

    # Determine Scenario Mode
    if any(w in question for w in ["compare", "vs", "versus", "difference"]):
        mode = "comparison"
        filters["compare_current"] = filters.get("compare_current", this_month)
        filters["compare_previous"] = filters.get("compare_previous", last_month)
    elif any(w in question for w in ["how much", "summary", "total", "each"]):
        mode = "consumption"
    else:
        mode = "discovery"

    # Use the ID passed from the API or default to C001
    c_id = state.get("customer_id") or filters.get("customer_id", "C001")
    digits = re.sub(r"\D", "", str(c_id))
    customer_id = f"C{int(digits):03d}"

    return {
        "filters": filters,
        "customer_id": customer_id,
        "mode": mode
    }

# -----------------------------
# Node 2: Vector Retrieval (with Blacklist)
# -----------------------------
@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        f = state.get("filters", {})
        mode = state.get("mode")
        c_id = state.get("customer_id")
        
        # --- BLACKLIST LOGIC ---
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
            return_properties=[
                "product_name", "added_sugar", "protein", "calories", "category", "date_consumed"
            ]
        )

        # Apply the "Post-Retrieval" Blacklist filter
        results = [
            obj.properties for obj in response.objects 
            if obj.properties.get("product_name") not in blacklist
        ]
        
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
        curr_p = filters.get("compare_current")
        prev_p = filters.get("compare_previous")
        
        comp_agg = {"current": {"protein": 0, "sugar": 0, "count": 0}, 
                    "previous": {"protein": 0, "sugar": 0, "count": 0}}
        
        for item in results:
            date_val = item.get("date_consumed")
            if not date_val: continue
            dt_str = str(date_val)[:7] # YYYY-MM format
            
            target = None
            if dt_str == curr_p: target = "current"
            elif dt_str == prev_p: target = "previous"
            
            if target:
                comp_agg[target]["protein"] += item.get("protein", 0)
                comp_agg[target]["sugar"] += item.get("added_sugar", 0)
                comp_agg[target]["count"] += 1
        
        return {"aggregates": comp_agg}

    # Consumption Analysis
    analysis = {}
    for item in results:
        date_val = item.get("date_consumed")
        if not date_val: continue
        dt = datetime.fromisoformat(str(date_val).replace('Z', '+00:00'))
        t_key = dt.strftime("%Y-%m")

        if t_key not in analysis: analysis[t_key] = {}
        cat = item.get("category", "general")
        if cat not in analysis[t_key]:
            analysis[t_key][cat] = {"protein": 0, "sugar": 0, "count": 0}

        analysis[t_key][cat]["protein"] += item.get("protein", 0)
        analysis[t_key][cat]["sugar"] += item.get("added_sugar", 0)
        analysis[t_key][cat]["count"] += 1

    return {"aggregates": analysis}

# -----------------------------
# Node 4: Coaching Engine (Excludes Dislikes)
# -----------------------------
@traceable(name="Coaching_Engine")
async def coaching_node(state: AgentState):
    mode = state.get("mode")
    agg = state.get("aggregates", {})
    feedback = state.get("user_feedback") or {}
    disliked_items = feedback.get("disliked_products", [])
    
    if mode != "comparison" or "current" not in agg:
        return {"recommendations": []}

    recs = []
    curr_prot = agg["current"].get("protein", 0)
    prev_prot = agg["previous"].get("protein", 0)

    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        
        # Always recommend high protein, but exclude disliked names
        base_filter = Filter.by_property("protein").greater_than(15.0)
        if disliked_items:
            base_filter = base_filter & Filter.by_property("product_name").contains_none(disliked_items)

        if curr_prot < prev_prot:
            prot_response = collection.query.hybrid(
                query="high protein healthy staples",
                filters=base_filter,
                limit=2
            )
            recs.extend([obj.properties for obj in prot_response.objects])

    unique_recs = list({r['product_name']: r for r in recs}.values())
    return {"recommendations": unique_recs}

# -----------------------------
# Node 5: Re-Ranking
# -----------------------------
@traceable(name="Re_Ranking")
async def ranker_node(state: AgentState):
    results = state.get("results", [])
    filters = state.get("filters", {})
    max_sugar = filters.get("max_sugar")
    
    if max_sugar is not None:
        results = [r for r in results if r.get("added_sugar", 999) < max_sugar]
    
    ranked = sorted(results, key=lambda x: (-x.get("protein", 0), x.get("added_sugar", 999)))
    return {"ranked_results": ranked}

# -----------------------------
# Node 6: Answer Generation
# -----------------------------
@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    mode = state.get("mode")
    agg = state.get("aggregates", {})
    recs = state.get("recommendations", [])

    if mode == "comparison":
        curr, prev = agg.get("current"), agg.get("previous")
        if not curr or not prev or (curr['count'] == 0 and prev['count'] == 0):
            return {"answer": "Insufficient data in the requested periods to perform a comparison."}
        
        p_diff = curr['protein'] - prev['protein']
        answer = (
            f"### ⚔️ Comparison: {state['filters'].get('compare_current')} vs {state['filters'].get('compare_previous')}\n"
            f"- **Protein:** {curr['protein']:.1f}g vs {prev['protein']:.1f}g ({'📈' if p_diff > 0 else '📉'} {abs(p_diff):.1f}g)\n"
            f"- **Activity:** {curr['count']} vs {prev['count']} items."
        )
        if recs:
            rec_names = ", ".join([f"**{r['product_name']}**" for r in recs])
            answer += f"\n\n**💡 Coach's Insight:** To boost your protein, try {rec_names}."
        return {"answer": answer}

    if mode == "consumption":
        if not agg: return {"answer": "No records found."}
        lines = ["### 📊 Consumption Report:"]
        for period, categories in sorted(agg.items()):
            lines.append(f"\n📅 **{period}**")
            for cat, s in categories.items():
                lines.append(f"- {cat.capitalize()}: {s['count']} items | Prot: {s['protein']:.1f}g")
        return {"answer": "\n".join(lines)}

    results = state.get("ranked_results", [])
    if not results: return {"answer": "No matches found."}
    res_text = "\n".join(f"- {r['product_name']}: {r['added_sugar']}g sugar, {r['protein']}g protein" for r in results[:5])
    return {"answer": f"### 🔍 Top Product Matches:\n{res_text}"}

# -----------------------------
# Graph compilation
# -----------------------------
# -----------------------------
# Async App Factory (FIX)
# -----------------------------
DB_PATH = "nutricart_checkpoints.db"

workflow = StateGraph(AgentState)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("aggregate", aggregation_node)
workflow.add_node("coach", coaching_node)
workflow.add_node("rank", ranker_node)
workflow.add_node("generate", generate_node)

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "aggregate")
workflow.add_edge("aggregate", "coach")
workflow.add_edge("coach", "rank")
workflow.add_edge("rank", "generate")
workflow.add_edge("generate", END)

async def get_app():
    conn = await aiosqlite.connect(DB_PATH)
    memory = AsyncSqliteSaver(conn)
    app = workflow.compile(checkpointer=memory)
    return app, conn
