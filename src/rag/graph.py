import logging
from typing import TypedDict, List, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from src.rag.parser import extract_normalized_filters
import weaviate
from weaviate.classes.query import Filter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

# Setup Logging
logger = logging.getLogger(__name__)

# 1. Define State
class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[dict[str, Any]]
    answer: str
    aggregates: dict[str, Any]
    user_id: str

# 2. Initialize LLM
#llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)
# Initialize both models
#primary_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)
backup_llm = ChatOllama(model="llama3.2:3b", temperature=0)

async def robust_llm_call(prompt: str) -> str:
    """Tries Gemini; falls back to Ollama on Quota/Network error."""
    try:
        response = await backup_llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            logger.warning("⚠️ Gemini Quota Hit. Falling back to Local Ollama...")
            response = await backup_llm.ainvoke(prompt)
            return response.content
        else:
            # Re-raise if it's a different, critical error
            raise 

# 3. Nodes
@traceable(name="Node: Unit_Normalization")
async def extraction_node(state: AgentState):
    filters = await extract_normalized_filters(state["question"])
    return {"filters": filters}

@traceable(name="Node: Weaviate_Retrieval")
async def retrieval_node(state: AgentState):
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    try:
        collection = client.collections.get("Product")
        f = state.get("filters", {})
        
        # Build Native Weaviate Filters
        weaviate_filter = None
        if "max_sugar" in f:
            weaviate_filter = Filter.by_property("added_sugar").less_than(float(f["max_sugar"]))
        if "min_protein" in f:
            p_filt = Filter.by_property("protein").greater_or_equal(float(f["min_protein"]))
            weaviate_filter = (weaviate_filter & p_filt) if weaviate_filter else p_filt
        if "max_calories" in f:
            c_filt = Filter.by_property("calories").less_than(float(f["max_calories"]))
            weaviate_filter = (weaviate_filter & c_filt) if weaviate_filter else c_filt

        # Execute semantic search WITH native filters
        response = collection.query.near_text(
            query=state["question"],
            filters=weaviate_filter,
            limit=5,
            return_properties=["product_name", "added_sugar", "protein", "calories"]
        )
        
        results = [obj.properties for obj in response.objects]
        return {"results": results}
    except Exception as e:
        logger.error(f"Retrieval Error: {e}")
        return {"results": []}
    finally:
        client.close()

@traceable(name="Node: Nutritional_Aggregation")
async def aggregation_node(state: AgentState):
    results = state.get("results", [])
    summary = {}

    for item in results:
        # Assuming your Weaviate 'Product' class has a 'category' property
        cat = item.get("category", "Uncategorized")
        
        if cat not in summary:
            summary[cat] = {"calories": 0, "protein": 0, "sugar": 0, "count": 0}
        
        summary[cat]["calories"] += item.get("calories", 0)
        summary[cat]["protein"] += item.get("protein", 0)
        summary[cat]["sugar"] += item.get("added_sugar", 0)
        summary[cat]["count"] += 1

    return {"aggregates": summary}

"""@traceable(name="Node: Answer_Synthesis")
async def generate_node(state: AgentState):
    results = state.get("results", [])
    filters = state.get("filters", {}) # Get the actual filter values
    
    if not results:
        return {"answer": "I found no products matching your specific limits."}

    context = "\n".join([
        f"- {p['product_name']}: {p['added_sugar']}g sugar, {p['protein']}g protein" 
        for p in results
    ])
    
    # Explicitly tell the LLM what the limits were
    # Inside generate_node in graph.py
    prompt = (
        "You are a Nutrition Assistant. Summarize these products based on the user's limits.\n"
        "Example Logic: 'Product A (2g sugar) meets the < 5g limit.'\n"
        f"User Request: {state['question']}\n"
        f"Limits: Sugar < {filters.get('max_sugar')}g, Protein > {filters.get('min_protein')}g.\n"
        f"Data:\n{context}\n"
        "Summarize only the items that truly meet the limits."
    )
    
    answer_text = await robust_llm_call(prompt)
    return {"answer": answer_text}"""

@traceable(name="Node: Answer_Synthesis")
async def generate_node(state: AgentState):
    agg = state.get("aggregates", {})
    user = state.get("user_id", "Unknown Consumer")
    
    if not agg:
        return {"answer": f"No consumption data found for Consumer {user}."}

    # Build a text-based table or list for the LLM to summarize
    breakdown = ""
    for cat, stats in agg.items():
        breakdown += (f"- {cat}: {stats['calories']} kcal, {stats['protein']}g Protein, "
                     f"{stats['sugar']}g Sugar ({stats['count']} items)\n")

    prompt = (
        f"You are a Nutrition Intelligence Dashboard. Summarize the consumption for {user}.\n"
        "Provide a high-level insight (e.g., 'Your highest protein source is Dairy').\n"
        f"Category Breakdown:\n{breakdown}\n"
        "Keep the tone professional and data-driven."
    )
    
    answer_text = await robust_llm_call(prompt)
    return {"answer": answer_text}

# 4. Build Graph
workflow = StateGraph(AgentState)

# Define all nodes
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("aggregate", aggregation_node)  # Your new node
workflow.add_node("generate", generate_node)

# Define the linear flow
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "aggregate")   # Flow moves TO aggregation
workflow.add_edge("aggregate", "generate")   # Flow moves TO synthesis
workflow.add_edge("generate", END)           # End the process

# 5. Compile with Persistence
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)