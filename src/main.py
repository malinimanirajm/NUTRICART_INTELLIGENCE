from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag.graph import app_graph  # Import the compiled LangGraph
from src.rag.ingester1 import ingest_data
import os
from dotenv import load_dotenv  # Correct import name

load_dotenv()

app = FastAPI(title="NutriCart Intelligence API v2")

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"status": "online", "version": "2.0 (Agentic)"}

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # We invoke the entire Graph. 
        # This triggers: Extract (mg->g) -> Retrieve (Weaviate) -> Generate
        initial_state = {"question": request.question}
        
        # Using ainvoke for asynchronous support
        final_state = await app_graph.ainvoke(initial_state)
        
        return {
            "question": final_state["question"],
            "filters_applied": final_state.get("filters"), # Shows the mg->g conversion
            "elaborated_answer": final_state.get("answer"), # THE NEW LLM DESCRIPTION
            "product_matches": final_state.get("results") # Your final RAG answer
        }
    except Exception as e:
        # Detailed error for debugging your new Graph nodes
        print(f"Graph Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Graph Execution Error")

# Keep your ingestion endpoint as is
@app.post("/ingest")
async def trigger_ingestion():
    try:
        ingest_data()
        return {"message": "✅ Data ingestion successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

