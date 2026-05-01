# 🛒 NutriCart Intelligence: Safety-First Nutrition AI

NutriCart Intelligence is an advanced RAG (Retrieval-Augmented Generation) agent built with **LangGraph**. It serves as a personal nutrition assistant that helps users discover products, compare nutritional values, and analyze their consumption history across weekly, monthly, and yearly intervals.

## 🌟 Key Features

### 1. Multi-Mode Intelligence
The agent dynamically switches between three operational modes based on user intent:
*   **Discovery:** Finding new products based on dietary constraints (e.g., "Find low sugar snacks").
*   **Comparison:** Side-by-side nutritional analysis (e.g., "Compare Product A vs Product B").
*   **Analysis:** Historical consumption reports (Weekly, Monthly, Yearly) calculating total protein, sugar, and calorie intake.

### 2. Dual-Layer Privacy Vault
To ensure enterprise-grade security, the system separates public product data from sensitive user info:
*   **Vector Library (Weaviate):** Stores product embeddings and consumption logs for high-speed semantic search and aggregation.
*   **Relational Vault (SQLite):** A secure, local database containing PII (Personally Identifiable Information) like emails and phone numbers, accessed only at the final delivery stage.

### 3. Automated Safety Guardrails
*   **Input Guard:** Detects and blocks prompt injections and non-nutrition queries.
*   **Output Validator:** Fact-checks AI responses against raw database results to eliminate hallucinations.
*   **Outbound Guard:** Automatically redacts internal database IDs and filters out restricted medical advice before transmission.

---

## 🏗️ Architecture

The agent follows a sophisticated graph-based workflow to ensure every response is verified and secure.



---

## 📂 Project Structure

```text
NURICART_INTELLIGENCE/
├── src/
│   ├── rag/
│   │   ├── graph.py          # LangGraph orchestration and logic
│   │   ├── parser.py         # LLM-based intent & filter extraction
│   │   └── config.py         # Centralized paths and API settings
│   ├── utils/
│   │   └── init_db.py        # SQLite Vault & Log table initializer
├── data/
│   └── raw/                  # Source CSV files (products & nutrition)
├── nutricart_vault.db        # Secure local SQLite database
└── test_graph.py             # End-to-end integration test suite
```

---

## 🛠️ Getting Started

### 1. Prerequisites
*   **Docker:** For running Weaviate.
*   **Ollama:** For local LLM processing (Llama 3.2:3b).
*   **Python 3.10+**

### 2. Installation
```bash
# Install dependencies
pip install langgraph weaviate-client aiosqlite langchain_ollama langchain_google_genai

# Initialize the Secure Vault
python3 src/utils/init_db.py
```

### 3. Infrastructure
Launch the vector database:
```bash
docker-compose up -d
```

---

## 📊 Usage & Testing

To run a full system verification—including a nutrition analysis report simulation—run:

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 test_graph.py
```

### Example Analysis Query
> "How much protein have I consumed this month?"

1.  **Parser** identifies `mode="consumption"` and `granularity="monthly"`.
2.  **Graph** retrieves logs for the specific `customer_id` from the last 30 days.
3.  **Aggregator** calculates totals and formats a Markdown report.
4.  **WhatsApp Node** simulates sending the report to the verified user in the Vault.

---

## 🛡️ Safety Compliance
This project implements a **Strict Redaction Policy**. Any response containing banned medical terminology (e.g., "cure," "prescribe") is automatically intercepted and blocked. Internal system identifiers are swapped for generic "Customer" labels in all outbound communications.