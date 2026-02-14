from fastapi import FastAPI
from pydantic import BaseModel
# Import the ALREADY compiled graph object from your generator file
from src.rag.generator import app 

api = FastAPI(title="NutriCart Intelligence API")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

@api.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    # CHANGE THIS LINE:
    # result = app({"question": request.query, ...})  <-- WRONG
    
    # TO THIS:
    result = app.invoke({"question": request.query, "context": "..."}) # <-- RIGHT
    
    return QueryResponse(answer=result["answer"])