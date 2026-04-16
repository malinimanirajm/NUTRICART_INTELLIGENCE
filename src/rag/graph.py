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


async def run_test_rag():
    print("🚀 Initializing 100% Local NutriCart Test Suite...")

    # 1. Initialize Local Judge (Ollama)
    # Ensure you've run 'ollama pull llama3' and 'ollama pull nomic-embed-text'
    judge_llm = ChatOllama(model="llama3", temperature=0)
    judge_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 2. Get the Compiled App and DB Connection
    app_graph, conn = await get_app()

    # 3. Define the "Golden Dataset"
    # Testing different scenario modes: Comparison, Consumption, and Filtered Discovery
    test_cases = [
        {
            "question": "Compare my protein for April vs March.",
            "ground_truth": "In April 2026, protein was Xg compared to Yg in March 2026.",
            "customer_id": "C0146"
        },
        {
            "question": "Give me a summary of everything I ate each month",
            "ground_truth": "The report should show consumption totals grouped by month for customer C0146.",
            "customer_id": "C0146"
        },
        {
            "question": "Find snacks with less than 5g sugar and high protein",
            "ground_truth": "Matches should only include items from the snack category with <5g sugar.",
            "customer_id": "C0146"
        }
    ]

    evaluation_results = []

    print(f"📊 Running inference on {len(test_cases)} cases...")

    for case in test_cases:
        # Prepare state matching your AgentState TypedDict
        inputs = {
            "question": case["question"],
            "customer_id": case["customer_id"],
            "user_feedback": {"disliked_products": []}, # Default empty blacklist
            "results": [],
            "ranked_results": [],
            "aggregates": {},
            "recommendations": []
        }
        
        # Unique thread for each test case
        config = {"configurable": {"thread_id": f"test_{case['customer_id']}"}}

        try:
            # Execute Graph
            response = await app_graph.ainvoke(inputs, config=config)
            
            evaluation_results.append({
                "question": case["question"],
                "answer": response.get("answer", "No answer generated"),
                "contexts": [str(c) for c in response.get("results", [])],
                "ground_truth": case["ground_truth"]
            })
            print(f"✅ Finished: {case['question'][:30]}...")
            
        except Exception as e:
            print(f"❌ Graph Error on '{case['question']}': {e}")

    # 4. Cleanup Graph Connection
    await conn.close()

    if not evaluation_results:
        print("🛑 No results to evaluate. Exiting.")
        return

    # 5. Score with RAGAS (Local)
    print("⚖️ Scoring results with Llama3 (Local)...")
    dataset = Dataset.from_list(evaluation_results)
    
    # max_workers=1 prevents CPU/RAM exhaustion during heavy local grading
    run_config = RunConfig(timeout=90, max_retries=3, max_workers=1)

    score = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=run_config
    )

    # 6. Professional Output
    print("\n" + "="*50)
    print("✨ RAG TEST COMPLETE ✨")
    print("="*50)
    df = score.to_pandas()
    print(df[['question', 'faithfulness', 'answer_relevancy', 'context_precision']])
    
    # Save for your records/GitHub evidence
    df.to_csv("test_rag_results.csv", index=False)
    print("\n💾 Detailed scores saved to test_rag_results.csv")

if __name__ == "__main__":
    try:
        asyncio.run(run_test_rag())
    except Exception as e:
        print(f"🚀 Main execution error: {e}")