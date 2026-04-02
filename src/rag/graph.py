import logging
import re
from typing import TypedDict, List, Any, Optional
from datetime import datetime

import weaviate
from weaviate.classes.query import Filter
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from langchain_ollama import ChatOllama

from src.rag import config
from src.rag.parser import extract_normalized_filters

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -----------------------------
# State
# -----------------------------
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    ranked_results: List[dict[str, Any]]
    aggregates: dict[str, Any]
    recommendations: List[dict[str, Any]]  # <--- NEW
    answer: str
    customer_id: str
    mode: str
    user_feedback: dict

# -----------------------------
# LLM
# -----------------------------
llm = ChatOllama(model=config.OLLAMA_MODEL, temperature=0)

# -----------------------------
# Node 1: Extraction
# -----------------------------
@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    question = state["question"]
    filters = await extract_normalized_filters(question) or {}

    if not filters.get("max_sugar"):
        sugar_match = re.search(r"less than (\d+)g", question.lower())
        if sugar_match:
            filters["max_sugar"] = float(sugar_match.group(1))

    # Scenario Logic
    if any(w in question.lower() for w in ["compare", "vs", "versus", "difference"]):
        mode = "comparison"
    elif any(w in question.lower() for w in ["how much", "summary", "total", "each"]):
        mode = "consumption"
    else:
        mode = "discovery"

    c_id = filters.get("customer_id", "C001")
    digits = re.sub(r"\D", "", str(c_id))
    customer_id = f"C{int(digits):03d}"

    return {
        "filters": filters,
        "customer_id": customer_id,
        "mode": mode
    }

# -----------------------------
# Node 2: Retrieval
# -----------------------------
@traceable(name="Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        f = state.get("filters", {})
        mode = state.get("mode")
        c_id = state.get("customer_id")

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
            limit=150, # Sufficient for dual-period comparison
            return_properties=[
                "product_name", "added_sugar", "protein", "calories", "category", "date_consumed"
            ]
        )

        results = [obj.properties for obj in response.objects]
        return {"results": results}

# -----------------------------
# Node 3: Aggregation (Multi-Scenario)
# -----------------------------
@traceable(name="Hybrid_Aggregation")
async def aggregation_node(state: AgentState):
    results = state.get("results", [])
    filters = state.get("filters", {})
    mode = state.get("mode")
    
    if mode == "comparison":
        curr_p = filters.get("compare_current")
        prev_p = filters.get("compare_previous")
        
        logger.info(f"DEBUG: Comparing periods: '{curr_p}' vs '{prev_p}' | Total items fetched: {len(results)}")

        # Format: { "current": stats, "previous": stats }
        comp_agg = {"current": {"protein": 0, "sugar": 0, "count": 0}, 
                    "previous": {"protein": 0, "sugar": 0, "count": 0}}
        
        for item in results:
            date_val = item.get("date_consumed")
            if not date_val: continue
            dt_str = str(date_val)[:7] # YYYY-MM
            
            target = None
            if dt_str == curr_p: target = "current"
            elif dt_str == prev_p: target = "previous"
            
            if target:
                comp_agg[target]["protein"] += item.get("protein", 0)
                comp_agg[target]["sugar"] += item.get("added_sugar", 0)
                comp_agg[target]["count"] += 1
        
        return {"aggregates": comp_agg}

    # Default Scenario 2 (Monthly/Weekly)
    granularity = filters.get("granularity", "monthly")
    analysis = {}
    for item in results:
        date_val = item.get("date_consumed")
        if not date_val: continue
        dt = datetime.fromisoformat(str(date_val).replace('Z', '+00:00'))

        t_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}" if granularity == "weekly" else dt.strftime("%Y-%m")
        if t_key not in analysis: analysis[t_key] = {}
        
        cat = item.get("category", "general")
        if cat not in analysis[t_key]:
            analysis[t_key][cat] = {"calories": 0, "protein": 0, "sugar": 0, "count": 0}

        analysis[t_key][cat]["protein"] += item.get("protein", 0)
        analysis[t_key][cat]["sugar"] += item.get("added_sugar", 0)
        analysis[t_key][cat]["count"] += 1

    return {"aggregates": analysis}

# -----------------------------
# Node 4: Re-ranker
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
# Node 5: Multi-Scenario Generation
# -----------------------------
@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    mode = state.get("mode")
    agg = state.get("aggregates", {})
    c_id = state.get("customer_id")
    recs = state.get("recommendations", [])

    if mode == "comparison":
        curr = agg.get("current")
        prev = agg.get("previous")
        
        if not curr or not prev or (curr['count'] == 0 and prev['count'] == 0):
            return {"answer": "Insufficient data in the requested periods to perform a comparison."}
        
        p_diff = curr['protein'] - prev['protein']
        s_diff = curr['sugar'] - prev['sugar']
        
        # Base Comparison Answer
        answer = (
            f"### ⚔️ Comparison: {state['filters'].get('compare_current')} vs {state['filters'].get('compare_previous')}\n"
            f"- **Protein:** {curr['protein']:.1f}g vs {prev['protein']:.1f}g ({'📈' if p_diff > 0 else '📉'} {abs(p_diff):.1f}g)\n"
            f"- **Sugar:** {curr['sugar']:.1f}g vs {prev['sugar']:.1f}g ({'⚠️' if s_diff > 0 else '✅'} {abs(s_diff):.1f}g)\n"
            f"- **Activity:** {curr['count']} item{'s' if curr['count'] != 1 else ''} vs {prev['count']} item{'s' if prev['count'] != 1 else ''}."
        )

        # SCENARIO 4: Append Coaching Insight if recommendations were found
        if recs:
            rec_names = ", ".join([f"**{r['product_name']}**" for r in recs])
            answer += (
                f"\n\n**💡 Coach's Insight:** I noticed your protein intake dropped compared to the previous period. "
                f"To help bridge this gap, you might consider adding {rec_names} to your next cart."
            )
        
        return {"answer": answer}

    if mode == "consumption":
        if not agg: 
            return {"answer": f"No records found for {c_id}."}
        
        lines = [f"### 📊 Consumption Report for {c_id}:"]
        # Sorting periods to ensure chronological order (e.g., 2024-09 before 2024-12)
        for period, categories in sorted(agg.items()):
            lines.append(f"\n📅 **{period}**")
            for cat, s in categories.items():
                lines.append(f"- {cat.capitalize()}: {s['count']} item{'s' if s['count'] != 1 else ''} | Prot: {s['protein']:.1f}g")
        
        return {"answer": "\n".join(lines)}

    # Default Scenario 1: Discovery
    results = state.get("ranked_results", [])
    if not results: 
        return {"answer": "No matches found for your search criteria."}
    
    res_text = "\n".join(f"- {r['product_name']}: {r['added_sugar']}g sugar, {r['protein']}g protein" for r in results[:5])
    return {"answer": f"### 🔍 Top Product Matches:\n{res_text}"}

@traceable(name="Coaching_Engine")
async def coaching_node(state: AgentState):
    mode = state.get("mode")
    agg = state.get("aggregates", {})
    question = state.get("question", "").lower()
    
    # Exit early if not a comparison or no data to analyze
    if mode != "comparison" or "current" not in agg:
        return {"recommendations": []}

    recs = []
    curr_prot = agg["current"].get("protein", 0)
    prev_prot = agg["previous"].get("protein", 0)

    # Open connection once for all potential "Rescue" queries
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        
        # TRIGGER 1: Protein Drop Logic
        if curr_prot < prev_prot:
            prot_response = collection.query.hybrid(
                query="high protein healthy staples",
                filters=Filter.by_property("protein").greater_than(15.0),
                limit=2
            )
            recs.extend([obj.properties for obj in prot_response.objects])

        # TRIGGER 2: Sugar Reduction Logic ("Goal-Seeker")
        if "sugar" in question and ("cut" in question or "reduce" in question or "goal" in question):
            sugar_response = collection.query.hybrid(
                query="zero sugar high protein alternatives",
                filters=Filter.by_property("added_sugar").equal(0.0),
                limit=3
            )
            # Use extend to add to existing recs if both triggers hit
            recs.extend([obj.properties for obj in sugar_response.objects])
        # NEW: Get the blacklist from state
    disliked_items = state.get("user_feedback", {}).get("disliked_products", [])
    
    with weaviate.connect_to_local(...) as client:
        collection = client.collections.get(config.COLLECTION_NAME)
        
        # Build the dynamic filter
        base_filter = Filter.by_property("protein").greater_than(15.0)
        
        # If there are dislikes, add a "NOT IN" condition
        if disliked_items:
            base_filter = base_filter & Filter.by_property("product_name").contains_none(disliked_items)

        response = collection.query.hybrid(
            query="high protein healthy staples",
            filters=base_filter,
            limit=2
        )

    # Deduplicate in case the same item hit both queries
    unique_recs = {r['product_name']: r for r in recs}.values()
    
    return {"recommendations": list(unique_recs)}
# -----------------------------
# Graph Build
# -----------------------------
workflow = StateGraph(AgentState)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("aggregate", aggregation_node)
workflow.add_node("rank", ranker_node)
workflow.add_node("generate", generate_node)
workflow.add_node("coach", coaching_node)

# 2. Update the edges (Aggregate -> Coach -> Rank)
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "aggregate")
workflow.add_edge("aggregate", "coach")  # <--- New transition
workflow.add_edge("coach", "rank")
workflow.add_edge("rank", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile(checkpointer=MemorySaver())