import asyncio
import pandas as pd
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.run_config import RunConfig
from langchain_ollama import ChatOllama, OllamaEmbeddings
from src.rag.graph import app_graph

async def run_eval():
    print("🧊 Starting Ultra-Low Resource Evaluation...")
    
    # 1. Configuration: Use a smaller model if Llama3 is too heavy
    # Llama 3.2 3B is much lighter than 8B if your laptop still heats up
    JUDGE_MODEL = "llama3.2:3b" 
    EMBED_MODEL = "nomic-embed-text"

    test_cases = [
        {"question": "Compare my protein intake in March vs January.", "reference": "User C146 consumed more protein in March than Jan.", "customer_id": "C146"},
        {"question": "Find high protein snacks.", "reference": "Should list high protein items for C146.", "customer_id": "C146"}
    ]

    # --- STAGE 1: SERIAL INFERENCE ---
    # We do not use asyncio.gather here to keep CPU spikes low
    prepared_data = []
    print(f"📊 Stage 1: Running Inference (Serial Mode)...")
    
    for case in test_cases:
        response = await app_graph.ainvoke({
            "question": case["question"], 
            "customer_id": case["customer_id"], 
            "user_feedback": {"disliked_products": []}
        })
        
        ctx = [f"Product: {r.get('product_name')} | Prot: {r.get('protein')}g" 
               for r in (response.get("results") or [])]

        prepared_data.append({
            "user_input": case["question"],
            "response": response.get("answer", ""),
            "retrieved_contexts": ctx if ctx else ["No data"],
            "reference": case["reference"]
        })
        # Physical break for the CPU
        await asyncio.sleep(1) 

    dataset = Dataset.from_list(prepared_data)

    # --- STAGE 2: BATCHED SCORING ---
    # We split metrics to let Ollama clear memory between runs
    print("\n⚖️  Stage 2: Scoring Metrics (One-by-One)...")
    
    # 1 Worker + High Timeout = Minimal thermal throttling
    run_config = RunConfig(timeout=300, max_workers=1)
    
    # Pass 1: Faithfulness (LLM only)
    print("  Evaluating Faithfulness...")
    judge_llm = ChatOllama(model=JUDGE_MODEL, temperature=0, num_predict=256)
    res_f = evaluate(dataset, metrics=[faithfulness], llm=judge_llm, run_config=run_config)
    
    # Force a 5-second cooldown to let fans catch up and VRAM clear
    await asyncio.sleep(5)

    # Pass 2: Relevancy (Embedding + LLM)
    print("  Evaluating Answer Relevancy...")
    judge_embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    res_r = evaluate(dataset, metrics=[answer_relevancy], llm=judge_llm, embeddings=judge_embeddings, run_config=run_config)

    # Final Merge
    df_f = res_f.to_pandas()
    df_r = res_r.to_pandas()
    final_df = df_f.merge(df_r[['user_input', 'answer_relevancy']], on='user_input')

    print("\n" + "❄️"*15)
    print("EVALUATION COMPLETE (NO MELTDOWN)")
    print(final_df[['user_input', 'faithfulness', 'answer_relevancy']])
    final_df.to_csv("cold_eval_results.csv", index=False)

if __name__ == "__main__":
    asyncio.run(run_eval())