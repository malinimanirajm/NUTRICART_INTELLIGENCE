import os
from typing import Annotated, TypedDict, List
from guardrails.hub import DetectPII
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
import weaviate
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from langgraph.checkpoint.memory import MemorySaver
from operator import add
from guardrails import Guard
import warnings
from pydantic import BaseModel, Field
from typing import Optional


warnings.filterwarnings("ignore", category=DeprecationWarning, module="guardrails")
warnings.filterwarnings("ignore", category=UserWarning, module="guardrails")

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    data_found: Annotated[List[dict], add]

def run_pii_guardrail(text: str) -> str:
    guard = Guard().use(
        DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="exception")
    )
    try:
        result = guard.validate(text)
        return text if result.validation_passed else "[PII Redacted for Security]"
    except Exception:
        return "[PII Redacted for Security]"

# 2. Logic & Nodes
llm = ChatOllama(model="llama3.1")


# 1. Add this Schema definition
class NutritionFilter(BaseModel):
    max_calories: Optional[float] = Field(None, description="Maximum calories per 100g")
    min_protein: Optional[float] = Field(None, description="Minimum protein in grams")
    max_sugar: Optional[float] = Field(None, description="Maximum sugar in grams")

# 2. Update the Analytics Node
@traceable
def analytics_node(state: AgentState):
    print("--- Analytics Agent Active (Dynamic Filter) ---")
    data = state.get("data_found", [])
    user_query = state["messages"][-1].content
    
    # Extract criteria using the model
    # Note: Ensure your LLM supports with_structured_output
    extractor = llm.with_structured_output(NutritionFilter)
    filters = extractor.invoke(f"Extract nutritional limits from: {user_query}")
    
    transactions = [i for i in data if i.get("data_type") == "transaction"]
    
    # Dynamic filter application
    filtered = transactions
    if filters.max_calories:
        filtered = [i for i in filtered if float(i.get("calories_100g", 0) or 0) <= filters.max_calories]
    if filters.min_protein:
        filtered = [i for i in filtered if float(i.get("protein_g", 0) or 0) >= filters.min_protein]
        
    if not filtered:
        return {"messages": [("assistant", "No transactions matched your criteria.")]}
    
    total_protein = sum(float(item.get("protein_g", 0) or 0) for item in filtered)
    total_sugar = sum(float(item.get("added_sugar_g", 0) or 0) for item in filtered)
    
    summary = f"Analysis: For {len(filtered)} items, Total Protein is {total_protein}g and Total Sugar is {total_sugar}g."
    return {"messages": [("assistant", run_pii_guardrail(summary))]}

def _search_weaviate_logic(query: str):
    client = weaviate.connect_to_local()
    try:
        collection = client.collections.get("NutricartUnified")
        # Added strict filter for transaction data to prevent PDF leakage
        response = collection.query.hybrid(query=query + " data_type:transaction", limit=5)
        return [obj.properties for obj in response.objects]
    finally:
        client.close()
@traceable
@traceable
def inventory_node(state: AgentState):
    print("--- Inventory Agent Active ---")
    user_query = state["messages"][-1].content
    
    # 1. Fetch data
    results = _search_weaviate_logic(user_query + " data_type:product")
    
    if not results:
        return {"messages": [("assistant", "I couldn't find any snacks matching that description in our inventory.")]}

    # 2. Format the list for the user
    # Assuming your Weaviate objects have 'brand_name' and 'content' or 'category_name'
    item_list = "\n".join([f"- {item.get('brand_name', 'Unknown Brand')}: {item.get('content', 'No details available')}" for item in results])
    
    summary = f"I found {len(results)} snacks for you:\n{item_list}"
    
    return {
        "data_found": results, 
        "messages": [("assistant", summary)]
    }
@traceable
def researcher_node(state: AgentState):
    print("--- Researcher Agent Active ---")
    user_query = state["messages"][-1].content
    results = _search_weaviate_logic(user_query) 
    return {"data_found": results, "messages": [("assistant", f"Researcher found {len(results)} items.")]}


def input_validator_node(state: AgentState):
    user_query = state["messages"][-1].content
    allowed = ["snacks", "protein", "sugar", "nutritional", "purchases"]
    if not any(topic in user_query.lower() for topic in allowed):
        return {"messages": [("assistant", "I'm sorry, I can only help with grocery inquiries.")]}
    return {}

def supervisor_router(state: AgentState):
    print("--- Supervisor Router Deciding Path ---")
    query = state["messages"][-1].content.lower()
    
    # Intent 1: Calculations
    if any(w in query for w in ["calculate", "total", "sum"]):
        return "analytics"
    
    # Intent 2: Product/Inventory Lookup
    if any(w in query for w in ["list", "inventory", "available", "products", "grocery","sugar","protein"]):
        return "inventory"
    
    # Default: Transaction Lookup
    return "researcher"

# 3. Graph Wiring
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", lambda state: {}) # Empty node
workflow.add_node("researcher", researcher_node)
workflow.add_node("analytics", analytics_node)
workflow.add_node("validator", input_validator_node)
workflow.add_node("inventory", inventory_node)

# Clean, single-path flow
workflow.add_edge(START, "validator")
workflow.add_conditional_edges("validator", lambda state: "supervisor" if "assistant" not in str(state["messages"][-1]) else END, {"supervisor": "supervisor", "END": END})
workflow.add_conditional_edges("supervisor", supervisor_router, {"researcher": "researcher", "analytics": "analytics","inventory": "inventory"})
workflow.add_edge("researcher", END)
workflow.add_edge("analytics", END)
workflow.add_edge("inventory", END)

# Persistent Memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)