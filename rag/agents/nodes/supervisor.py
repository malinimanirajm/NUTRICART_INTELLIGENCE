# src/agents/nodes/supervisor.py
from langchain_openai import ChatOpenAI
from src.agents.state import AgentState

def supervisor_node(state: AgentState):
    """Orchestrates traffic by analyzing inputs and updating execution states."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    system_prompt = (
        "You are the Supervisor for NutriCart. Analyze user input.\n"
        "If they want to review, complain, or leave text product feedback, select 'preferences_agent'.\n"
        "If they want a summary of historical stats, past metrics, or to check their progress reports/PDFs, select 'data_mining_agent'.\n"
        "If the loop is finished and the final response is complete, select 'FINISH'.\n"
        "Respond ONLY with the name of the selection target."
    )
    messages = [("system", system_prompt)] + state["messages"]
    prediction = llm.invoke(messages).content.strip()
    
    return {"next_node": prediction}