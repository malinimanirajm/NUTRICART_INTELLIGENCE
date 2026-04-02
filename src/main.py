import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Ensure your project structure is correctly in the PYTHONPATH
from src.rag.graph import app_graph
from src.rag.ingester import ingest_data

load_dotenv()

app = FastAPI(
    title="NutriCart Intelligence API v2.1",
    description="Agentic RAG with Adaptive Human-in-the-Loop Feedback."
)

# --- Models ---
class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_session"

class FeedbackRequest(BaseModel):
    product: str
    action: str  # e.g., "dislike" or "like"
    thread_id: str

# --- In-Memory Feedback Store (For local dev) ---
# In a full production app, this would be a table in SQLite or PostgreSQL
user_feedback_store = {} 

@app.get("/")
async def root():
    return {
        "status": "online", 
        "version": "2.1 (Adaptive)",
        "capabilities": ["Discovery", "Analytics", "Comparison", "Coaching", "Feedback"]
    }

@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # Retrieve existing dislikes for this thread to pass into the Graph
        dislikes = user_feedback_store.get(request.thread_id, {}).get("disliked_products", [])
        
        # Initial state now includes the user's past feedback
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
async def save_feedback(feedback: FeedbackRequest):
    """Updates the thread's memory with user preferences."""
    try:
        if feedback.thread_id not in user_feedback_store:
            user_feedback_store[feedback.thread_id] = {"disliked_products": [], "liked_products": []}
        
        if feedback.action == "dislike":
            if feedback.product not in user_feedback_store[feedback.thread_id]["disliked_products"]:
                user_feedback_store[feedback.thread_id]["disliked_products"].append(feedback.product)
        
        print(f"📝 [FEEDBACK] Thread {feedback.thread_id} updated: Disliked {feedback.product}")
        return {"status": "success", "message": f"Updated preferences for {feedback.product}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback Failed: {str(e)}")

@app.post("/ingest")
async def trigger_ingestion():
    try:
        ingest_data()
        return {"message": "✅ Data ingestion and indexing successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion Failed: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)