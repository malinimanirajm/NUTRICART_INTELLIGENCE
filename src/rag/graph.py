from typing import TypedDict, List, Any, Optional
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from src.rag.parser import extract_normalized_filters # Ensure path is correct
import weaviate
from weaviate.classes.query import Filter
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import logging

logger = logging.getLogger(__name__)

# Define the shared state
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    answer: str

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@traceable(name="Node: Unit_Normalization")
async def extraction_node(state: AgentState):
    filters = await extract_normalized_filters(state["question"])
    return {"filters": filters}

@traceable(name="Node: Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    # Using 127.0.0.1 is more stable for local Docker on macOS
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    try:
        collection = client.collections.get("Product")
        
        weaviate_filter = None
        f = state.get("filters", {})
        logger.info(f"DEBUG: Filters from state: {f}")

        if "max_sugar" in f:
            weaviate_filter = Filter.by_property("added_sugar").less_than(float(f["max_sugar"]))
            logger.info(f"DEBUG: Applied max_sugar filter: {f['max_sugar']}")
        if "min_protein" in f:
            p_filt = Filter.by_property("protein").greater_or_equal(float(f["min_protein"]))
            weaviate_filter = (weaviate_filter & p_filt) if weaviate_filter else p_filt
            logger.info(f"DEBUG: Applied min_protein filter: {f['min_protein']}")

        # Query with near_text, then filter results in Python
        if f:
            logger.info(f"DEBUG: Querying with near_text and Python-based filtering...")
            # First get results with near_text (semantic search)
            response = collection.query.near_text(
                query="product",
                limit=50,  # Get more to filter
                return_properties=["product_name", "added_sugar", "protein", "calories"]
            )
            # Filter results in Python based on numeric criteria
            filtered_results = []
            for obj in response.objects:
                props = obj.properties
                # Apply filter logic
                if "max_sugar" in f and props.get("added_sugar", 999) >= float(f["max_sugar"]):
                    continue
                if "min_protein" in f and props.get("protein", 0) < float(f["min_protein"]):
                    continue
                filtered_results.append(props)
                if len(filtered_results) >= 5:
                    break
            results = filtered_results
            logger.info(f"DEBUG: Retrieved {len(results)} filtered results")
        else:
            logger.info(f"DEBUG: Fetching all products with near_text...")
            response = collection.query.near_text(
                query="product",
                limit=5,
                return_properties=["product_name", "added_sugar", "protein", "calories"]
            )
            results = [obj.properties for obj in response.objects]
            logger.info(f"DEBUG: Retrieved {len(results)} results")
        return {"results": results}
    finally:
        client.close()

@traceable(name="Node: Answer_Synthesis")
async def generate_node(state: AgentState):
    results = state.get("results", [])
    
    # Handle empty results gracefully
    if not results:
        return {"answer": "I couldn't find any products matching those criteria in our database. Try a different search?"}

    context = "\n".join([f"- {p['product_name']}: {p['added_sugar']}g sugar, {p['protein']}g protein" for p in results])
    prompt = f"Summarize why these products fit the request '{state['question']}':\n{context}"
    response = await llm.ainvoke(prompt)
    return {"answer": response.content}

# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("generate", generate_node)

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()