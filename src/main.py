import os
import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# --- NEW: Import your SQL utilities ---
from src.utils.db import init_db, save_dislike, get_dislikes

# Ensure your project structure is correctly in the PYTHONPATH
from src.rag.graph import app_graph
from src.rag.ingester import ingest_data

load_dotenv()

app = FastAPI(
    title="NutriCart Intelligence API v2.2",
    description="Agentic RAG with Persistent SQLite Feedback Memory."
)

# --- Models ---
class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_session"

class FeedbackRequest(BaseModel):
    product: str
    action: str  # e.g., "dislike"
    thread_id: str

# --- DB Initialization on Startup ---
@app.on_event("startup")
async def startup_event():
    """Ensure the SQLite file and tables are created before the API starts."""
    try:
        # 1. Initialize the Long-Term Vault (Preferences/Dislikes)
        fix_empty_vault() 
        
        # 2. Initialize any other DBs (like Checkpoints if needed)
        # init_db() 

        print("✅ Database Vault: Initialized and Tables Ready.")
        print("🚀 NutriCart Intelligence: API Engine Online.")
        
    except Exception as e:
        print(f"❌ Critical Startup Error: {e}")
        # In production, you might want the app to stop if the DB fails

@app.get("/")
async def root():
    return {
        "status": "online", 
        "version": "2.2 (Persistent)",
        "capabilities": ["Discovery", "Analytics", "Comparison", "Coaching", "Feedback", "SQLite_Vault"]
    }

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # --- UPDATE: Fetch dislikes from SQLite instead of a dictionary ---
        dislikes = get_dislikes(request.thread_id)
        
        initial_state = {
            "question": request.question,
            "user_feedback": {"disliked_products": dislikes} 
        }
        
        config = {"configurable": {"thread_id": request.thread_id}}
        
        final_state = await app_graph.ainvoke(initial_state, config=config)
        
        return {
            "session_id": request.thread_id,
            "question": final_state.get("question"),
            "mode": final_state.get("mode"),
            "filters_applied": final_state.get("filters"),
            "elaborated_answer": final_state.get("answer"),
            "recommendations": final_state.get("recommendations", []),
            "product_matches": final_state.get("ranked_results", [])[:5]
        }
    except Exception as e:
        print(f"❌ Graph Execution Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal AI Logic Error: {str(e)}"
        )

@app.post("/feedback")
async def save_feedback(customer_id: str, product_name: str, feedback_type: str):
    """Endpoint to save likes/dislikes to the Vault."""
    conn = sqlite3.connect("nutricart_vault.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_feedback (customer_id, product_name, feedback_type) VALUES (?, ?, ?)",
        (customer_id, product_name, feedback_type)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Saved {feedback_type} for {product_name}"}

@app.post("/ingest")
async def trigger_ingestion():
    try:
        ingest_data()
        return {"message": "✅ Data ingestion and indexing successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion Failed: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)