import os
import sqlite3
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# --- FIXED: Importing from src/utils/init_db.py ---
# We match the filename (init_db) and the function (fix_empty_vault)
from src.utils.init_db import fix_empty_vault, get_dislikes

# RAG and Graph imports
from src.rag.graph import app_graph
from src.rag.ingester import ingest_data

load_dotenv()

# In src/rag/graph.py # or whatever your variable name is

# --- MODERN: Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown without the deprecation warning."""
    try:
        # This matches the function name in your init_db.py
        fix_empty_vault()
        print("✅ Database Vault: Initialized and Tables Ready.")
        print("🚀 NutriCart Intelligence: API Engine Online.")
    except Exception as e:
        print(f"❌ Critical Startup Error: {e}")
    
    yield  # The application is now running
    
    print("🚀 NutriCart Intelligence: Shutting down.")

app = FastAPI(
    title="NutriCart Intelligence API v2.2",
    description="Agentic RAG with Persistent SQLite Feedback Memory.",
    lifespan=lifespan
)

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_session"

# --- Endpoints ---
@app.get("/")
async def root():
    return {
        "status": "online", 
        "version": "2.2 (Persistent)",
        "capabilities": ["Discovery", "Analytics", "Coaching", "Feedback", "SQLite_Vault"]
    }

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # Fetch long-term 'Substance' (dislikes) from the Vault
        # We use thread_id as the customer_id for now
        dislikes = get_dislikes(request.thread_id)
    
        # DEBUG PRINT (Check your terminal after running)
        print(f"🔍 DEBUG: Blacklist for {request.thread_id} is: {dislikes}")
    
        initial_state = {
        "question": request.question,
        "user_feedback": {"disliked_products": dislikes} 
        }
        
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Invoke the LangGraph Agent
        final_state = await app_graph.ainvoke(initial_state, config=config)
        
        return {
            "session_id": request.thread_id,
            "elaborated_answer": final_state.get("answer"),
            "product_matches": final_state.get("ranked_results", [])[:5]
        }
    except Exception as e:
        print(f"❌ Graph Execution Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def save_feedback(customer_id: str, product_name: str, feedback_type: str):
    """Directly writing user preferences to the Vault."""
    # Note: In a production app, use the DB_PATH from init_db.py here too
    conn = sqlite3.connect("nutricart_vault.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_feedback (customer_id, product_name, feedback_type) VALUES (?, ?, ?)",
            (customer_id, product_name, feedback_type)
        )
        conn.commit()
        return {"status": "success", "message": f"Saved {feedback_type} for {product_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)