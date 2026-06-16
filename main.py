from rag.agents.agent_system import app
from langchain_core.messages import HumanMessage
import os

# Enable LangSmith Tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your_api_key_here"  # Get this from smith.langchain.com
os.environ["LANGCHAIN_PROJECT"] = "Nutricart-Intelligence"



def chat_with_agent(user_input):
    # This invokes the graph with your message
    # LangGraph will run the supervisor, then route to researcher or analytics
    result = app.invoke({"messages": [HumanMessage(content=user_input)]})
    
    # Print the final conversation history
    print("\n--- Final Conversation History ---")
    for msg in result["messages"]:
        print(f"{msg.type.upper()}: {msg.content}")

if __name__ == "__main__":
    # Test 1: Route to researcher
    chat_with_agent("Find me recent purchases of NatureNest snacks")
    
    # Test 2: Route to analytics
    chat_with_agent("Calculate total protein from my recent purchases")