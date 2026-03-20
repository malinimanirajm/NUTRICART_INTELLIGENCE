import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.rag.graph import app_graph
from src.rag.ingester import ingest_data

load_dotenv()

app = FastAPI(title="NutriCart Intelligence API v2")

class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_session" # Added for memory support

@app.get("/")
async def root():
    return {"status": "online", "version": "2.0 (Agentic)"}

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # Initial state for the Graph
        initial_state = {"question": request.question}
        
        # Config for LangGraph Persistence (Memory)
        # Using the thread_id allows the agent to remember context for that specific user
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Execute the Graph
        final_state = await app_graph.ainvoke(initial_state, config=config)
        
        return {
            "session_id": request.thread_id,
            "question": final_state.get("question"),
            "filters_applied": final_state.get("filters"),
            "elaborated_answer": final_state.get("answer"),
            "product_matches": final_state.get("results")
        }
    except Exception as e:
        print(f"Graph Execution Error: {e}")
        raise HTTPException(status_code=500, detail="Internal AI Logic Error")

@app.post("/ingest")
async def trigger_ingestion():
    try:
        ingest_data()
        return {"message": "✅ Data ingestion and indexing successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))