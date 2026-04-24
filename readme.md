To reflect your recent architectural hardening, I’ve updated your `README.md` to include the **Guardrails**, the **Safe-Routing logic**, and the **LLMOPs** enhancements.

---

# NutriCart Intelligence v2.5 🛒
**Enterprise-Grade Agentic RAG for Precision Nutrition & Analytics**

NutriCart Intelligence is a stateful, safety-hardened AI engine designed to transform grocery data into reliable health insights. Unlike standard RAG systems, NutriCart utilizes an **Agentic Graph** to handle complex reasoning, temporal comparisons (2024-anchored), and persistent user memory.

---

## 🛡️ New: Multi-Layer Guardrails
To ensure production-grade reliability, the system now features a specialized safety pipeline:
* **Input Guardrails:** Intercepts prompt injections and off-topic queries before they reach the LLM.
* **Output Validation:** A "Fact-Checker" node that cross-references AI-generated responses against retrieved data to eliminate hallucinations.
* **Safe Routing:** Conditional graph logic that blocks malicious paths and triggers self-correction loops.

---

## ✨ Core Features

* **Agentic Orchestration:** Built with **LangGraph** to manage stateful nodes for extraction, retrieval, and coaching.
* **Temporal Intelligence:** Reference-anchored logic to handle historical 2024 data inquiries from a 2026 runtime.
* **Hybrid Vector Search:** Optimized **Weaviate** queries (Alpha 0.2) combining semantic meaning with exact keyword SKU filtering.
* **Invisible Personalization:** A SQLite-backed "Vault" that remembers user dislikes to filter recommendations automatically.
* **Resource-Conscious Evals:** Integrated **RAGAS** suite with serial execution to prevent CPU thermal throttling on local hardware.

---

## 🏗️ Technical Stack & LLMOPs

* **Orchestration:** LangGraph (Stateful Logic)
* **LLM Engine:** Dual-model setup (Ollama local-first, Google Gemini fallback)
* **Vector DB:** Weaviate
* **Relational DB:** SQLite (State Checkpointing & Feedback Vault)
* **Observability:** LangSmith (Trace Auditing & Evaluation)
* **API:** FastAPI (Asynchronous Engine)

---

## 📂 Updated Project Structure

```text
├── src/
│   ├── rag/
│   │   ├── graph.py       # Hardened Graph with Guardrail Nodes
│   │   ├── parser.py      # Dual-model filter extraction logic
│   │   ├── config.py      # Environment & ID padding configs
│   │   └── security.py    # Sanitizers & Injection detection
│   ├── utils/
│   │   └── init_db.py     # SQLite persistence & Vault setup
│   └── main.py            # FastAPI entry point with SQLite Vault hooks
├── tests/
│   └── eval_rag.py        # Serialized RAGAS suite (No-Meltdown Mode)
├── data/                  # 2024 SKU & Nutrition datasets
└── requirements.txt       # Dependency manifest
```

---

## 🔧 Installation & Setup

1. **Ingest Data:**
   ```bash
   python -m src.rag.ingester  # Refreshes Weaviate with optimized schemas
   ```

2. **Start the API:**
   ```bash
   python main.py
   ```

3. **Query the Agent:**
   ```bash
   curl -X POST "http://localhost:8000/ask" \
   -H "Content-Type: application/json" \
   -d '{"thread_id": "C001", "question": "Find snacks with < 5g sugar"}'
   ```

---

## ⚖️ Evaluation & Quality Control

The system implements **LLMOPs** best practices via the `eval_rag.py` suite. It evaluates:
* **Faithfulness:** Does the answer match the retrieved product data?
* **Answer Relevancy:** Does the response actually address the user's nutritional goal?
* **Context Precision:** Are the top-ranked products in the retrieval the most relevant?

---

## 🔒 Security Policy

NutriCart utilizes a **Zero-Trust Input Model**. Every query is analyzed by the `guard_node` for injection patterns (e.g., "ignore previous instructions") and domain relevance (Nutrition/Grocery only). Failure to pass these checks results in an immediate safety-halt.

---