from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from src.rag.parser import extract_normalized_filters

class AgentState(TypedDict):
    question: str
    filters: dict
    results: List[str]

@traceable(name="Node: Unit_Normalization")
async def extraction_node(state: AgentState):
    # This node turns "500mg" into "0.5"
    filters = await extract_normalized_filters(state["question"])
    return {"filters": filters}

@traceable(name="Node: Weaviate_Retrieval")
def retrieval_node(state: AgentState):
    # Here you would call your existing search_nutricart(state["filters"])
    return {"results": ["Verified_Product_ID_123"]}

# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("extract", extraction_node)
workflow.add_node("retrieve", retrieval_node)

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", END)

app_graph = workflow.compile()