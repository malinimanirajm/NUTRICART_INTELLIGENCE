# src/agents/nodes/preferences.py
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from src.agents.state import AgentState
from src.utils.db import save_product_feedback

@tool
def record_feedback_tool(product_id: str, product_name: str, feedback_type: str, text: str, ctx: AgentState) -> str:
    """Saves user feedback or textual product reviews straight into the database."""
    save_product_feedback(
        customer_id=ctx["customer_id"],
        product_id=product_id,
        product_name=product_name,
        feedback_type=feedback_type,
        feedback_text=text
    )
    return f"Successfully saved customer review for {product_name}."

def preferences_node(state: AgentState):
    """Handles parsing and writing user product reviews."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools([record_feedback_tool])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}