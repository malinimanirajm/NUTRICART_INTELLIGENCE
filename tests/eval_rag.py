import asyncio
import aiosqlite
import pandas as pd
from datasets import Dataset

# Ragas v1 imports
from ragas import evaluate
from ragas.metrics.collections import (
    faithfulness,
    answer_relevancy,
    context_precision,
)

# Ollama + LangChain
from langchain_ollama import ChatOllama, OllamaEmbeddings

# LangGraph memory
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# Your workflow
from src.rag.graph import get_app


async def run_evaluations():
    DB_PATH = "nutricart_checkpoints.db"

    print("🚀 Starting Local NutriCart Evaluation (Ollama)...")

    # ✅ Open connection manually (safer than context manager)
    app_graph, conn = await get_app()

    results = []

    # ✅ Expanded dataset (add more for better evaluation)
    test_data = [
        {
            "question": "Show me dairy items with high protein.",
            "ground_truth": "High protein dairy items include DairyPure_Item_30 and HomeBest_Item_16."
        },
        {
            "question": "Recommend low calorie snacks.",
            "ground_truth": "Low calorie snacks include items with fewer calories such as light chips or diet snack options."
        },
        {
            "question": "What are some healthy breakfast options?",
            "ground_truth": "Healthy breakfast options include oats, fruits, yogurt, and high-protein cereals."
        }
    ]

    for item in test_data:
        inputs = {
            "question": item["question"],
            "customer_id": "C0146",
            "user_feedback": {"disliked_products": []},
            "results": [],
            "ranked_results": [],
            "aggregates": {},
            "recommendations": [],
        }

        config = {"configurable": {"thread_id": "eval_test_thread"}}

        try:
            # ✅ Timeout protection
            response = await asyncio.wait_for(
                app_graph.ainvoke(inputs, config=config),
                timeout=60,
            )

            # ✅ Safe answer fallback
            answer = response.get("answer") or "No answer generated."

            contexts = response.get("results", [])
            contexts = [str(c) for c in contexts] if contexts else ["No context retrieved"]

            results.append(
                {
                    "question": item["question"],
                    "answer": answer,
                    "contexts": contexts,
                    "ground_truth": item["ground_truth"],
                }
            )

        except Exception as e:
            print(f"❌ Error during ainvoke: {e}")

    # Close DB connection
    await conn.close()

    if not results:
        print("⚠️ No results gathered. Check Weaviate/Ollama setup.")
        return

    # ✅ Setup Ragas Judge (Local)
    langchain_llm = ChatOllama(model="llama3")
    langchain_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    dataset = Dataset.from_list(results)

    print("⚖️ Judging responses...")

    score = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=langchain_llm,
        embeddings=langchain_embeddings,
    )

    print("\n✅ Evaluation Complete!")

    df = score.to_pandas()

    print("\n📊 Scores:")
    print(df[["question", "faithfulness", "answer_relevancy", "context_precision"]])

    # ✅ Save results
    df.to_csv("eval_results.csv", index=False)
    print("\n💾 Results saved to eval_results.csv")


if __name__ == "__main__":
    try:
        asyncio.run(run_evaluations())
    except RuntimeError as e:
        print(f"Loop error: {e}")