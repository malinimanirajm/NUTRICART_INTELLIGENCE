import asyncio
import pandas as pd
from datasets import Dataset

# Ragas v1 Metrics
from ragas import evaluate
from ragas.metrics.collections import (
    faithfulness,
    answer_relevancy,
    context_precision,
)
from ragas.run_config import RunConfig

# Local Ollama Components
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Import the factory from your graph.py
from src.rag.graph import get_app

async def run_test_rag():
    print("🚀 Initializing 100% Local NutriCart Test Suite...")

    # 1. Force Local Judge (Ollama)
    # This ensures Ragas doesn't try to use Gemini/OpenAI
    judge_llm = ChatOllama(model="llama3", temperature=0)
    judge_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 2. Get the Compiled App
    app_graph, conn = await get_app()

    # 3. Your Test Cases
    test_cases = [
        {
            "question": "Compare my protein for April vs March.",
            "ground_truth": "In April 2026, protein was Xg compared to Yg in March 2026.",
            "customer_id": "C0146"
        }
    ]

    evaluation_results = []

    for case in test_cases:
        inputs = {
            "question": case["question"],
            "customer_id": case["customer_id"],
            "user_feedback": {"disliked_products": []},
            "results": [], "ranked_results": [], "aggregates": {}, "recommendations": []
        }
        
        try:
            # Run inference
            response = await app_graph.ainvoke(inputs, config={"configurable": {"thread_id": "test_thread"}})
            
            evaluation_results.append({
                "question": case["question"],
                "answer": response.get("answer", "No answer"),
                "contexts": [str(c) for c in response.get("results", [])],
                "ground_truth": case["ground_truth"]
            })
            print(f"✅ Generated answer for: {case['question']}")
        except Exception as e:
            print(f"❌ Graph Error: {e}")

    await conn.close()

    if not evaluation_results:
        return

    # 4. Run RAGAS Evaluation LOCALLY
    # max_workers=1 is CRITICAL for local LLMs to prevent crashing your RAM/CPU
    run_config = RunConfig(timeout=120, max_retries=3, max_workers=1)

    print("⚖️ Judging results locally with Llama3 (No API calls)...")
    
    dataset = Dataset.from_list(evaluation_results)
    
    score = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=judge_llm,           # <--- Overriding default (Gemini)
        embeddings=judge_embeddings, # <--- Overriding default (Gemini)
        run_config=run_config
    )

    print("\n📊 Final Local Scores:")
    print(score.to_pandas()[['question', 'faithfulness', 'answer_relevancy']])

if __name__ == "__main__":
    asyncio.run(run_test_rag())