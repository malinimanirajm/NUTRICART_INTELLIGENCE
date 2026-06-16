import os
from typing import Annotated, TypedDict, List
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

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    data_found: Annotated[List[dict], add]

# 2. Prompt Loader
@traceable
def load_system_prompt(agent_name):
    path = os.path.join("prompts", "system_prompt.txt")
    try:
        with open(path, "r") as f:
            content = f.read()
            start_tag = f"[{agent_name.upper()}_PROMPT]"
            start = content.find(start_tag) + len(start_tag)
            end = content.find("[", start) if content.find("[", start) != -1 else len(content)
            return content[start:end].strip()
    except Exception:
        return f"You are the {agent_name} agent."


# 4. Agent Nodes
llm = ChatOllama(model="llama3.1")

# 1. Define the logic as a clean, standard function
def _search_weaviate_logic(query: str):
    client = weaviate.connect_to_local()
    try:
        collection = client.collections.get("NutricartUnified")
        response = collection.query.hybrid(query=query, limit=3)
        return [obj.properties for obj in response.objects]
    finally:
        client.close()

# 2. Define the tool as a separate object for the LLM
@tool
def search_weaviate(query: str):
    """Search grocery transactions and nutritional PDF knowledge."""
    return _search_weaviate_logic(query)

# 3. Update your researcher_node to use the clean logic function
@traceable
def researcher_node(state: AgentState):
    print("--- Researcher Agent Active ---")
    user_query = state["messages"][-1].content
    
    # CALL THE LOGIC DIRECTLY, NOT THE TOOL OBJECT
    results = _search_weaviate_logic(user_query) 
    
    return {
        "data_found": results, 
        "messages": [("assistant", f"Researcher found {len(results)} items.")]
    }

@traceable
def analytics_node(state: AgentState):
    print("--- Analytics Agent Active ---")
    data = state.get("data_found", [])
    if not data:
        return {"messages": [("assistant", "No data available to analyze.")]}
    
    total_protein = sum(item.get("protein_g", 0) or 0 for item in data)
    summary = f"Analysis: Total Protein found in retrieved items is {total_protein}g."
    return {"messages": [("assistant", summary)]}

"""@traceable
def supervisor_node(state: AgentState):
    print("--- Supervisor Agent deciding next step ---")
    
    # 1. Load the prompt from your file
    system_instruction = load_system_prompt("SUPERVISOR")
    
    # 2. Create a prompt template that injects the system instruction
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "{user_query}")
    ])
    
    # 3. Create a chain
    chain = prompt_template | llm
    
    # 4. Get the user query
    user_query = state["messages"][-1].content
    
    # 5. Invoke the chain
    response = chain.invoke({"user_query": user_query})
    
    choice = response.content.strip().lower()
    return "analytics" if "analytics" in choice else "researcher"""

# The Node: Updates state, returns a dict
def supervisor_node(state: AgentState):
    print("--- Supervisor Node Updating State ---")
    return {"messages": []} 

# The Router: Decides path, returns a string (e.g., "researcher")
def supervisor_router(state: AgentState):
    print("--- Supervisor Router Deciding Path ---")
    system_instruction = load_system_prompt("SUPERVISOR")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "{user_query}")
    ])
    chain = prompt_template | llm
    user_query = state["messages"][-1].content
    response = chain.invoke({"user_query": user_query})
    
    choice = response.content.strip().lower()
    
    # IMPROVED ROUTING LOGIC
    if "calculate" in choice or "total" in choice or "trend" in choice:
        return "analytics"
    return "researcher"

# 5. Graph Wiring
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("analytics", analytics_node)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {"researcher": "researcher", "analytics": "analytics"}
)

workflow.add_edge("researcher", END)
workflow.add_edge("analytics", END)
memory = MemorySaver()

app = workflow.compile(checkpointer=memory)