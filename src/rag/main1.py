from ingester import ingest_data
from retriever import search_products
# --- UPDATE IMPORT ---
from generator import run_langgraph_generator 

def run_pipeline():
    # 1. Ingest Data (Run this only when data changes)
    ingest_data()
    
    # 2. Ask Question
    question = "Which products are high in protein and low in sugar?"
    
    # 3. Retrieve Context
    print(f"Retrieving context for: {question}")
    context = search_products(question)
    
    # 4. Generate Answer using LangGraph
    print("Generating answer with LangGraph...")
    # --- UPDATE CALL ---
    answer = run_langgraph_generator(question, context)
    
    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    run_pipeline()