
# NutriCart Intelligence 🛒
**AI-Driven Personal Nutrition & Grocery Analytics Engine**

NutriCart Intelligence is a stateful RAG (Retrieval-Augmented Generation) system designed to transform raw grocery data into actionable health insights. Built with **LangGraph**, **Weaviate**, and **Ollama**, it provides users with personalized consumption reports, protein-to-sugar comparisons, and an intelligent "Coaching Engine" that respects user-defined preferences and dislikes.

---

##  Key Features

* **Stateful AI Agent:** Managed via LangGraph to handle complex conversation flows and multi-step reasoning.
* **Vector Search RAG:** High-performance retrieval of nutritional data using Weaviate.
* **Dynamic Comparison Engine:** Real-time analysis of nutritional trends (e.g., Month-over-Month protein intake).
* **Invisible Personalization:** A SQLite-backed "Vault" that stores user feedback to automatically filter out disliked products from search results and coaching recommendations.
* **Company-Standard Evals:** Integrated **RAGAS** framework to measure Faithfulness, Relevance, and Precision using local LLM "Judges."

---

##  Technical Stack

* **Orchestration:** LangGraph (StateGraph)
* **LLM:** Ollama (Llama 3 / Mistral)
* **Database:** Weaviate (Vector), SQLite (Checkpoints & User Vault)
* **Framework:** FastAPI
* **Evaluation:** RAGAS & LangSmith

---

## 📂 Project Structure

```text
├── src/
│   ├── rag/
│   │   ├── graph.py       # Core LangGraph logic & nodes
│   │   ├── parser.py      # Intent & filter extraction logic
│   │   └── config.py      # Environment & API configurations
│   ├── utils/
│   │   ├── init_db.py     # SQLite persistence setup
│   │   └── email_sender.py # SMTP background task integration
│   └── main.py            # FastAPI entry point
├── tests/
│   └── eval_rag.py        # RAGAS evaluation suite
├── data/                  # Mock grocery & nutrition datasets
├── README.md              # Project documentation
└── requirements.txt       # Dependency manifest
```

---

## 🔧 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/nutricart-intelligence.git
    cd nutricart-intelligence
    ```

2.  **Set Up Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start Local Services:**
    Ensure **Ollama** and **Weaviate** are running:
    ```bash
    ollama serve
    # Ensure Weaviate is running on localhost:8080
    ```

---

##  Running Evaluations

To ensure the RAG system meets professional quality standards, run the evaluation suite:

```bash
python -m tests.eval_rag
```
This script evaluates the agent using local **Ollama** models as judges for **Faithfulness** and **Answer Relevancy**.

---

## Background Tasks: Email Updates

The system utilizes FastAPI's `BackgroundTasks` to send nutritional summaries without blocking the user interface.
* **Protocol:** SMTP via `aiosmtplib`
* **Trigger:** Automated after specific comparison queries or weekly digests.

---

##  Contribution

1.  Fork the project.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

