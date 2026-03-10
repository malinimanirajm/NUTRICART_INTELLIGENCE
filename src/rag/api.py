from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag.ingester import ingest_data
from src.rag.retriever import search_products
from src.rag.generator import run_langgraph_generator

app = FastAPI(title="NutriCart Intelligence API")

# Define the request structure
class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"status": "online", "message": "NutriCart Intelligence API is running"}

# 1. Endpoint to trigger data ingestion
@app.post("/ingest")
async def trigger_ingestion():
    try:
        ingest_data()
        return {"message": "✅ Data ingestion successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Endpoint for the AI Pipeline
@app.post("/ask")
async def ask_nutricart(request: QueryRequest):
    try:
        # Step 1: Retrieve Context from Weaviate
        context = search_products(request.question)
        
        # Step 2: Generate Answer using LangGraph
        answer = run_langgraph_generator(request.question, context)
        
        return {
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)