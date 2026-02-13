import ollama
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
import warnings

# Suppress ResourceWarning for unclosed sockets
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed <socket.socket")

# 1. Define the State
class AgentState(TypedDict):
    question: str
    context: str
    answer: str

# 2. Define the Node function (LLM Generation)
def generate_node(state: AgentState):
    prompt = f"""
    You are a nutrition intelligence assistant.
    Use the context below to answer the question accurately.
    If the answer is not in the context, say you don't know.

    Context:
    {state['context']}

    Question:
    {state['question']}

    Answer:
    """
    
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'user', 'content': prompt},
    ])
    
    # Explicitly close the Ollama client socket to prevent ResourceWarning
    if hasattr(ollama._client, '_client'):
        ollama._client._client.close()
        
    return {"answer": response['message']['content']}

# 3. Build the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("generator", generate_node)

# Set the entrypoint and exit point
workflow.set_entry_point("generator")
workflow.add_edge("generator", END)

# Compile the graph
app = workflow.compile()

# Function to run the graph
def run_langgraph_generator(question, context):
    final_state = app.invoke({"question": question, "context": context})
    return final_state["answer"]