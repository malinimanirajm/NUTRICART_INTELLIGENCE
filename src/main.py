import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure your project structure is correctly in the PYTHONPATH
from src.rag.graph import app_graph
from src.rag.ingester import ingest_data

load_dotenv()

app = FastAPI(
    title="NutriCart Intelligence API v2",
    description="Agentic RAG for Discovery, Analytics, Comparison, and Coaching."
)

class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_session"

@app.get("/")
async def root():
    return {
        "status": "online", 
        "version": "2.0 (Agentic)",
        "capabilities": ["Discovery", "Analytics", "Comparison", "Coaching"]
    }

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # Initial state for the Graph
        # We pass the question; the Graph handles the rest of the fields
        initial_state = {"question": request.question}
        
        # thread_id is the key for LangGraph's MemorySaver
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Execute the Graph (Async)
        final_state = await app_graph.ainvoke(initial_state, config=config)
        
        # We return a rich response including the mode and coaching recs
        return {
            "session_id": request.thread_id,
            "question": final_state.get("question"),
            "mode": final_state.get("mode"),
            "filters_applied": final_state.get("filters"),
            "elaborated_answer": final_state.get("answer"),
            "recommendations": final_state.get("recommendations", []), # Scenario 4
            "product_matches": final_state.get("ranked_results")[:5] # Top 5 ranked
        }
    except Exception as e:
        # Log the full error for debugging in your Anaconda terminal
        print(f"❌ Graph Execution Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal AI Logic Error: {str(e)}"
        )

@app.post("/ingest")
async def trigger_ingestion():
    """Manual trigger to re-index the Weaviate collection from CSV."""
    try:
        ingest_data()
        return {"message": "✅ Data ingestion and indexing successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion Failed: {str(e)}")
    
if __name__ == "__main__":
    # Running on localhost for your local dev environment
    uvicorn.run(app, host="127.0.0.1", port=8000)