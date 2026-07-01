from agents.agent_system import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from langsmith import traceable
load_dotenv()

@traceable
def chat_with_agent(user_message, thread_id):
    """
    Invokes the agent while maintaining thread state via thread_id.
    """
    # Using the same thread_id across turns ensures persistence
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id}
    }
    
    # Invoke the graph
    result = app.invoke(
        {"messages": [HumanMessage(content=user_message)]}, 
        config=config
    )
    
    # Print the last message from the assistant
    last_message = result["messages"][-1].content
    print(f"AI: {last_message}")
    return result

if __name__ == "__main__":
    # Define a single session ID for this conversation
    SESSION_ID = "cs0016_session_001"
    
    print(f"--- Starting Session: {SESSION_ID} ---")
    
    # First turn: Researcher collects data
   # print("\nUSER: Hi I am customer cs0023")
   # chat_with_agent("Hi I am customer cs0023", thread_id=SESSION_ID)
    
    # Second turn: Analytics agent sees the 'data_found' from the first turn
    print("\nUSER:Hi user cs0089 here Get me snacks  with at least 5g of protein and some insights or information about protein.")
    chat_with_agent("Hi user cs0089 here Get me snacks  with at least 5g of protein and some insights or information about protein.", thread_id=SESSION_ID)
    
    print(f"\nTracing enabled: {os.getenv('LANGSMITH_TRACING')}")
    print(f"Project name: {os.getenv('LANGSMITH_PROJECT')}")