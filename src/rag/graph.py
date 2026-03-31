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
    comparison_results: List[dict[str, Any]]
    answer: str
    aggregates: dict[str, Any]
    customer_id: str
    time_delta: Optional[int]
    mode: str

# -----------------------------
# LLM
# -----------------------------
llm = ChatOllama(model=config.OLLAMA_MODEL, temperature=0)


async def robust_llm_call(prompt: str) -> str:
    try:
        res = await llm.ainvoke(prompt)
        return res.content
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "Error generating answer."


# -----------------------------
# Node 1: Extraction
# -----------------------------
@traceable(name="Intent_Extraction")
async def extraction_node(state: AgentState):
    question = state["question"]
    filters = await extract_normalized_filters(question) or {}

    # Mode detection
    if any(w in question.lower() for w in ["compare", "vs", "versus"]):
        mode = "comparison"
    elif any(w in question.lower() for w in ["total", "consumed", "history"]):
        mode = "consumption"
    else:
        mode = "discovery"

    # Normalize customer_id
    c_id = filters.get("customer_id", "C001")
    digits = re.sub(r"\D", "", str(c_id))
    customer_id = f"C{int(digits):03d}"

    logger.info(f"Extraction filters: {filters}")
    return {
        "filters": filters,
        "customer_id": customer_id,
        "mode": mode,
        "time_delta": None
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

        if f.get("max_calories") is not None:
            filter_clauses.append(Filter.by_property("calories").less_than(float(f["max_calories"])))

        if f.get("category"):
            filter_clauses.append(Filter.by_property("category").equal(f["category"]))

        logger.info(f"Applied filters: {filter_clauses}")
        weaviate_filter = Filter.all_of(filter_clauses) if filter_clauses else None

        # -----------------------------
        # Hybrid search for precision + relevance
        # -----------------------------
        response = collection.query.hybrid(
            query=state["question"],
            filters=weaviate_filter,
            alpha=0.5,
            limit=20,
            return_properties=[
                "product_name",
                "added_sugar",
                "protein",
                "calories",
                "category",
                "date_consumed"
            ]
        )

        results = [obj.properties for obj in response.objects]

        # Hard post-filter
        if f.get("max_sugar") is not None:
            results = [r for r in results if r.get("added_sugar", 999) < f["max_sugar"]]

        logger.info(f"Retrieved {len(results)} results after filtering")
        return {"results": results, "comparison_results": []}


# -----------------------------
# Node 3: Aggregation
# -----------------------------
@traceable(name="Aggregation")
async def aggregation_node(state: AgentState):
    def summarize(items):
        summary = {}
        for item in items:
            cat = item.get("category", "general")
            if cat not in summary:
                summary[cat] = {"calories": 0, "protein": 0, "sugar": 0, "count": 0}

            summary[cat]["calories"] += item.get("calories", 0)
            summary[cat]["protein"] += item.get("protein", 0)
            summary[cat]["sugar"] += item.get("added_sugar", 0)
            summary[cat]["count"] += 1
        return summary

    return {"aggregates": {"current": summarize(state.get("results", [])), "previous": {}}}


# -----------------------------
# Node 4: Generation
# -----------------------------
def rank_products(results):
    return sorted(
        results,
        key=lambda x: (-x.get("protein", 0), x.get("added_sugar", 999), x.get("calories", 999))
    )


@traceable(name="Answer_Generation")
async def generate_node(state: AgentState):
    results = state.get("results", [])
    filters = state.get("filters", {})

    if not results:
        if filters.get("max_sugar"):
            return {"answer": f"No products found under {filters['max_sugar']}g sugar."}
        return {"answer": "No matching products found."}

    # Deterministic ranking
    ranked = rank_products(results)[:5]

    items = [
        {
            "product_name": r["product_name"],
            "added_sugar": r["added_sugar"],
            "protein": r["protein"],
            "calories": r["calories"],
            "category": r.get("category")
        }
        for r in ranked
    ]

    answer_text = "\n".join(
        f"- {r['product_name']}: {r['added_sugar']}g sugar, {r['protein']}g protein, {r['calories']} kcal"
        for r in ranked
    )

    return {
        "answer": f"Top products with sugar < {filters.get('max_sugar', 'requested')}g:\n{answer_text}",
        "items": items,
        "count": len(items),
        "filters_applied": filters
    }


# -----------------------------
# Graph Build
# -----------------------------
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