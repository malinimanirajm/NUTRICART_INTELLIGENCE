# src/agents/nodes/data_mining.py
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from src.agents.state import AgentState
from src.utils.db import get_historical_summary, get_latest_user_assets

@tool
def extract_nutrition_metrics_tool(time_frame: str, ctx: AgentState) -> str:
    """Queries relational tables to return historical nutrition items across structural windows ('week', 'month', 'year')."""
    raw_logs = get_historical_summary(ctx["customer_id"], time_frame=time_frame)
    if not raw_logs:
        return f"No transaction data found over the past {time_frame}."
    
    total_cal = sum(row[2] * float(row[3]) for row in raw_logs)
    total_prot = sum(row[2] * float(row[4]) for row in raw_logs)
    return f"Calculated totals over past {time_frame}: Calories: {total_cal}kcal, Protein: {total_prot}g."

@tool
def fetch_user_media_assets_tool(ctx: AgentState) -> dict:
    """Retrieves S3 public URLs for the user's latest generated PDF reports and nutrition charts."""
    assets = get_latest_user_assets(ctx["customer_id"])
    return f"Latest accessible assets: PDF URL: {assets['pdf']}, Image URL: {assets['image']}"

def data_mining_node(state: AgentState):
    """Handles structural timeframe aggregation lookups and asset tracking."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools([extract_nutrition_metrics_tool, fetch_user_media_assets_tool])
    response = llm_with_tools.invoke(state["messages"])
    
    # Check if tools extracted specific file links, and bind them back into state memory
    updated_state = {"messages": [response]}
    
    # Simple check to extract asset pointers back to state if found during execution
    assets = get_latest_user_assets(state["customer_id"])
    if assets["pdf"]:
        updated_state["attached_pdf_url"] = assets["pdf"]
    if assets["image"]:
        updated_state["attached_image_url"] = assets["image"]
        
    return updated_state