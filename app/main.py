from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.supervisor import supervisor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.

    Initialize shared resources here (Weaviate, LangSmith, Memory, etc.).
    """
    print("Starting NutriCart Intelligence...")

    yield

    print("Stopping NutriCart Intelligence...")


app = FastAPI(
    title="NutriCart Intelligence",
    description="Production-ready Agentic AI platform for intelligent grocery search and recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "application": "NutriCart Intelligence",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """
    Health endpoint.

    Later we'll also check:
        - Weaviate
        - Memory DB
        - Ollama
        - LangSmith
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


@app.post("/chat")
async def chat(request: dict):
    """
    All requests go through the Supervisor.
    """
    return await supervisor.run(request)