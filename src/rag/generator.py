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
    # We improved the prompt here to stop the "21g < 5g" hallucination
    prompt = f"""
    You are a strict Nutrition Intelligence Assistant.
    
    TASK:
    Analyze the provided product context and answer the user's question.
    
    CRITICAL RULE:
    You must verify the numbers. If a user asks for 'less than 5g sugar', 
    do NOT recommend a product with more than 5g sugar.
    
    Context:
    {state['context']}

    Question:
    {state['question']}

    Answer:
    """
    
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'user', 'content': prompt},
    ])
    
    return {"answer": response['message']['content']}

# 3. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("generator", generate_node)
workflow.set_entry_point("generator")
workflow.add_edge("generator", END)

# 4. Compile the graph (Named app_graph to match your API call)
app_graph = workflow.compile()

# 5. Function to run the graph
def run_langgraph_generator(question, context):
    # Ensure this uses app_graph.invoke
    final_state = app_graph.invoke({"question": question, "context": context})
    return final_state["answer"]