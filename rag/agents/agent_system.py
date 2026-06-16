import os
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
import weaviate
from langchain_core.prompts import ChatPromptTemplate

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    data_found: List[dict]

# 2. Prompt Loader
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

# 3. Tool Definitions
@tool
def search_weaviate(query: str):
    """Search grocery transactions and nutritional PDF knowledge."""
    client = weaviate.connect_to_local()
    collection = client.collections.get("NutricartUnified")
    response = collection.query.hybrid(query=query, limit=3)
    client.close()
    return [obj.properties for obj in response.objects]

# 4. Agent Nodes
llm = ChatOllama(model="llama3.1")

def researcher_node(state: AgentState):
    print("--- Researcher Agent Active ---")
    user_query = state["messages"][-1].content
    results = search_weaviate.invoke(user_query)
    return {"data_found": results, "messages": [("assistant", f"Researcher found {len(results)} items.")]}

def analytics_node(state: AgentState):
    print("--- Analytics Agent Active ---")
    data = state.get("data_found", [])
    if not data:
        return {"messages": [("assistant", "No data available to analyze.")]}
    
    total_protein = sum(item.get("protein_g", 0) or 0 for item in data)
    summary = f"Analysis: Total Protein found in retrieved items is {total_protein}g."
    return {"messages": [("assistant", summary)]}


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
    return "analytics" if "analytics" in choice else "researcher"

# 5. Graph Wiring
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("analytics", analytics_node)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    supervisor_node,
    {"researcher": "researcher", "analytics": "analytics"}
)
workflow.add_edge("researcher", END)
workflow.add_edge("analytics", END)

app = workflow.compile()