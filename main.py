from rag.agents.agent_system import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
# Load the .env file
load_dotenv()

# Use a consistent thread_id for the conversation session
THREAD_ID = "nature-nest-session-001"
CONFIG = {"configurable": {"thread_id": THREAD_ID}}

def chat_with_agent(user_input):
    # Pass the config to the invoke method
    result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=CONFIG)
    
    print("\n--- Final Conversation History ---")
    for msg in result["messages"]:
        print(f"{msg.type.upper()}: {msg.content}")

if __name__ == "__main__":
    # First turn: Researcher finds data and saves it to the state checkpoint
    chat_with_agent("Find me recent purchases of snacks for customer cs0016")
    
    # Second turn: Analytics agent loads the state from the checkpoint 
    # and sees the data found in the previous turn
    chat_with_agent("Calculate total protein and sugar from my recent purchases")
    print(f"Tracing enabled: {os.getenv('LANGSMITH_TRACING')}")
    print(f"Project name: {os.getenv('LANGSMITH_PROJECT')}")