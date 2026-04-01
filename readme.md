# Grocery Purchase–Based Nutrition Dataset (Synthetic)

## Description
This project generates a synthetic grocery dataset that links customer purchase history with nutrition information.  
It simulates grocery-app transaction data to enable nutrition and diet analysis without manual food logging.

---

## Dataset Summary
- 400 customers  
- Time period: Q1 2024 (Jan–Mar)  
- 1–5 purchases per customer per week  
- 6 product categories  
- 15 brands across all categories  

---
Since **NutriCart Intelligence** has evolved from a basic search tool into a sophisticated RAG pipeline with custom re-ranking and category normalization, your README should reflect that "Production-Ready" shift.

A great technical README for an AI engineer should highlight the **Architecture**, the **Data Pipeline**, and the **State Management**.

Here is a structured template for your `README.md` that captures everything we just built:

---

# 🍎 NutriCart Intelligence: Advanced RAG for Fitness

NutriCart Intelligence is a high-precision Retrieval-Augmented Generation (RAG) system designed to help users navigate complex nutritional data. It goes beyond simple keyword search by using **Semantic Category Mapping** and a **Multi-Stage Re-ranker** to prioritize high-protein, low-sugar options.

## 🚀 Key Features

* **Intelligent Intent Extraction:** Uses Gemini 2.0 Flash and Ollama to transform natural language queries (e.g., *"munchies under 5g sugar"*) into structured database filters.
* **Custom Category Mapping:** A proprietary mapping layer in the ingestion pipeline that normalizes brand-specific names into functional categories like `snack`, `dairy`, and `pantry`.
* **Fitness-First Re-ranking:** A deterministic ranking node that sorts retrieved items by **Protein Density** while strictly enforcing nutritional constraints (e.g., maximum sugar/calories).
* **Hybrid Search:** Combines Weaviate’s vector embeddings with keyword-based BM25 search for maximum retrieval accuracy.

---

## Architecture

The system is built using a **LangGraph** state machine to ensure a predictable and traceable data flow:

1.  **Extraction Node:** Normalizes user intent and extracts Pydantic-validated filters.
2.  **Retrieval Node:** Executes a Hybrid Search against a local **Weaviate** instance.
3.  **Aggregation Node:** Summarizes nutritional data for the current result set.
4.  **Ranker Node:** Applies a "Hard Filter" and sorts items by Protein-to-Sugar ratios.
5.  **Generation Node:** Produces a structured, natural language response.



---

## 🛠️ Tech Stack

* **Orchestration:** LangGraph / LangChain
* **Vector Database:** Weaviate (Local)
* **LLMs:** Gemini 2.0 Flash (Structured Output), Ollama (Llama 3.2 3b fallback)
* **Backend:** FastAPI
* **Environment:** Anaconda / Python 3.10+

---

## 📂 Project Structure

```text
├── src/
│   ├── rag/
│   │   ├── config.py       # Global settings and Weaviate config
│   │   ├── graph.py        # LangGraph workflow definition
│   │   ├── ingester.py     # Data pipeline with Category Mapping
│   │   └── parser.py       # Intent extraction and normalization
├── data/
│   └── raw/                # Source CSV nutrition and product data
├── main.py                 # FastAPI Entry point
└── README.md
```

---

## 🚦 Getting Started

1.  **Ingest Data:**
    ```bash
    python src/rag/ingester.py
    ```
2.  **Start the API:**
    ```bash
    uvicorn main:app --reload
    ```
3.  **Query the System:**
    ```bash
    curl -X 'POST' \
      'http://localhost:8000/query' \
      -H 'Content-Type: application/json' \
      -d '{"question": "get me snacks less than 5g of sugar"}'
    ```

Scenario,Mode,Purpose,Example Query
1,Discovery,Semantic search for products matching macro goals.,"""Find snacks < 5g sugar with 10g protein."""
2,Analytics,Time-based aggregation of a user's consumption history.,"""Show my weekly protein totals for C001."""
3,Comparison,Delta calculation between two specific time periods.,"""Compare my protein in March vs February."""
4,Coaching,(Beta) Proactive recommendations based on data gaps.,"""How can I fix my protein drop from last month?"""
