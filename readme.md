
# 📊 NutriCart Intelligence (v2.2 Persistent)

NutriCart Intelligence is an Enterprise-Grade Agentic Retrieval-Augmented Generation (RAG) platform designed to track, analyze, and discover food products based on strict clinical nutrition properties and consumer behavior. 

By combining a localized LLM graph orchestration layer with multi-engine storage (hybrid vector indices and long-term relational databases), the system transforms a traditional digital shopping cart into an interactive, compliance-guided health tracking ecosystem.

---

## 🏗️ Core Architectural Blueprint

NutriCart Intelligence is designed around an event-driven **State Machine** orchestrated via a single, unified graph using LangGraph. It decouples linguistic understanding, mathematical computations, and physical database lookups into strict execution boundaries.


```

[User Message Entry]
│
▼
┌─────────────────┐
│   guard_node    ├───────────► [Prompt Injection Attempt] ──► [Abrupt Stop / Rejection]
└────────┬────────┘
│ (Passes Verification)
▼
┌─────────────────┐
│ extraction_node ├───────────► Identifies Mode ("discovery", "consumption", "comparison")
└────────┬────────┘             & Granularity ("weekly", "monthly", "yearly")
│
▼
┌─────────────────┐
│ retriever_node  ├───────────► Fetches Hybrid Embeddings from Weaviate + SQL Context
└────────┬────────┘
│
├─────────────────────────────────────┐
▼ (if mode == "consumption")          ▼ (if mode == "discovery" / "comparison")
┌─────────────────┐                    ┌─────────────────┐
│ aggregation_node│                    │  generate_node  │
└────────┬────────┘                    └────────┬────────┘
│                                     │
└──────────────────┬──────────────────┘
│
▼
┌─────────────────┐
│ validation_node ├───────────► Cross-checks generated metrics vs. ground-truth databases
└────────┬────────┘
│
▼
┌─────────────────┐
│ send_whatsapp   ├───────────► Delivers verified alert payload via Twilio Integration
└─────────────────┘

```

---

## Deep-Dive Architectural & Engineering Q&A

### 1. Basic LLM App vs. Actual Agent
* **Basic LLM Application:** Follows a strict, linear pipeline ($User \rightarrow RAG \rightarrow LLM \rightarrow Output$). The LLM functions purely as a text-generator or semantic bridge; it has no control over its own execution flow or data retrieval mechanisms.
* **NutriCart Agentic Core:** Utilizes a non-linear state graph loop controlled by user intent. The system evaluates the initial request, sets graph-wide context parameters inside `AgentState`, dynamically alters runtime routing paths, and shifts between functional states (such as switching from conversational search to automated data compilation).

### 2. Operational Synchronization: Planning, Memory, and Tool Use
The orchestration architecture relies on a highly synchronized **ReAct (Reasoning and Acting)** loop paradigm:
* **Planning:** The extraction node breaks natural language inputs down into a clean, structured query profile (`NutritionFilters`) mapping targeted macro ceilings or statistical limits.
* **Memory:** The system features short-term operational state retention via LangGraph thread contexts, alongside long-term cross-session memory maintained through an isolated relational SQLite core.
* **Tool Access:** Rather than providing unmitigated freeform tool usage, the agent processes structured extracted parameters to query Weaviate hybrid indices, intercepting execution errors cleanly to guide downstream node choices.

### 3. Infinite Loop Mitigation: Why They Happen & How We Prevent It
* **The Vulnerability:** Traditional autonomous AI agents enter infinite loops when they hit a tool execution failure or format error, causing them to repeatedly invoke the exact same tool call with identical parameters expecting a fresh result.
* **Our Solution:** NutriCart Intelligence guarantees execution finality by utilizing **deterministic graph invariants**. The orchestration topology forces data through an explicit routing matrix (`route_after_retrieval`). Because state transitions are mathematically bound to distinct nodes (e.g., forcing historical data summaries straight to an isolated computation node), recursive model generation loops are structurally impossible.

### 4. Handling Tool Failures, Timeouts, and Bad Responses
In a production-ready agent environment, tools must not crash the application server. Our retrieval nodes wrap external data actions inside granular error-containment layers:
```python
try:
    with weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT) as client:
        # Vector/Hybrid search execution
        return {"results": [obj.properties for obj in response.objects]}
except Exception as e:
    logger.error(f"Database tool execution failure: {e}")
    return {"results": [], "safety_status": "blocked"}

```

If an endpoint connection drops or database pools timeout, the exception is gracefully caught, logging defaults are safely assigned (`"results": []`), and the graph safety flags transition to `"blocked"`, allowing downstream nodes to handle execution termination safely.

### 5. Preventing Double Bookings and Duplicate Actions

When non-deterministic models experience downstream transmission delays, they frequently hallucinate failures and re-trigger identical backend requests. NutriCart Intelligence mitigates duplicate processing by:

* Leveraging long-term unique thread state checks via centralized **LangGraph checkpoint tokens**.
* Enforcing a strict compound primary key constraint (`PRIMARY KEY (thread_id, product_name)`) inside the database schema, ensuring any re-delivered request overwrites or updates existing logs safely rather than creating duplicate entries.

### 6. Safety Barriers with Critical Real-World Data

Autonomous agents should never have unmitigated, blind write access to operational backends. Our system enforces separation of concerns:

* Direct model generations are kept isolated from customer records.
* Any structural interaction modifications (such as updating long-term user restrictions or blacklists) must pass through a strict micro-service endpoint layout (`/feedback`), which maps values directly via secure parameterization.

### 7. Scalability: Moving from 10 to 10,000 Requests/Day

To scale efficiently under intense concurrent usage, the application implements:

* **Fully Asynchronous State Operations:** Built using non-blocking Python async/await principles across the entire Graph architecture to maximize query throughput.
* **High-Efficiency Memory Caching:** Offloading contextual checks away from slow vector searches by maintaining a lightweight SQLite store for hyper-fast localized indexing.

### 8. Incorporating Humans-in-the-Loop (HITL)

* **The Strategy:** High-risk discrepancies—such as an automated nutritional fact alert missing core compliance metrics—must halt autonomous workflows before communicating with clients.
* **Implementation:** The architecture exposes an intermediate approval property (`is_approved`) in `AgentState`. The `outbound_guard_node` evaluates this flag; if validation fails, it pauses graph continuation, queues the operation state, and awaits explicit operator confirmation over admin interfaces before enabling outbound WhatsApp deployment.

### 9. Prompt and Workflow Versioning

Prompts and structural steps are abstracted entirely away from core endpoint code logic. Prompt configurations are isolated within `src/rag/prompts.py` and model parsing frameworks map directly to independent version states inside LangSmith registries, facilitating blue-green prompt deployments without risking system crashes.

### 10. Core Embedding Strategy

The system uses the **`text2vec-transformers`** semantic vector configuration model native to our local **Weaviate** database cluster. It vectorizes item profiles and executes hybrid queries blending dense semantic vectors with precise keyword indices at an exact $\alpha$ parameter of `0.5`.

### 11. Custom Chunking Optimization

Because our enterprise engine handles tabular database structures rather than long-form, unstructured essays, traditional character-count window splitting is rejected. Instead, the pipeline uses a **structured document-per-row representation strategy** inside `src/rag/ingester.py`.

* Rows from `products.csv` and `nutrition.csv` are joined on `product_id`.
* Attributes are compiled into a comprehensive, self-contained textual snapshot string:
`"{product_name}. Category: {category}. Protein: {protein}g. Sugar: {sugar}g. Calories: {calories} kcal. Consumed by {customer_id} on {consumption_date}."`
* This guarantees absolute context preservation with zero string fragmentation.

### 12. Cost-Optimization Invariants

1. **Local Inference Execution:** Uses a local instance of **Ollama (`llama3.2:3b`)** running at a zero-temperature setting for parsing, completely avoiding token-based pricing models.
2. **Defensive Fallback Triggers:** The cloud-hosted **Gemini-2.0-Flash-Lite** engine acts solely as a secondary failover backup, spinning up only when the local parser throws a Pydantic structure anomaly.
3. **Pre-Filter Execution Optimization:** User interaction constraints (like historical product dislikes) are pulled from SQLite before running database queries, reducing vector operations.

### 13. System Independence: Operating Without Agentic AI

**Yes, the core product can run entirely without an AI agent.** Because items feature explicit, clean relational categories and fixed numerical parameters, a traditional user interface with slider scales and dropdowns can map constraints directly into explicit code definitions (e.g., programmatically compiling a Weaviate `Filter.all_of()` structure), returning exact product listings deterministically without any LLM processing.

### 14. Model Context Protocol (MCP) Usage

The system does not utilize Model Context Protocol adapters. All infrastructure relies on native python driver clients connecting directly over localized TCP/IP endpoints (`weaviate.connect_to_local()` and `aiosqlite`).

### 15. Prompt Injection Immunity

The platform applies a robust two-layer security validation fence:

* **Input Gate (`security.py`):** Passes incoming user strings through a strict regex checking layer to identify common jailbreak patterns (e.g., *"ignore previous instructions"*).
* **Isolation of Parsing Scope:** User prompts are never given execution context within data backends; they are only used to populate specific fields in a strict data structure (`NutritionFilters`). Any injection text that slips through is processed harmlessly as a literal string filter value rather than code.

---

## 📁 System Repository Structure

```text
NUTRICART_INTELLIGENCE/
│
├── data/
│   └── raw/
│       └── q1_2024_v1/
│           ├── products.csv            # Enterprise inventory mapping
│           └── nutrition.csv           # Master ingredient & macro properties
│
├── src/
│   ├── rag/
│   │   ├── config.py                   # Global hardware, paths, and model settings
│   │   ├── graph.py                    # LangGraph orchestration state topology
│   │   ├── ingester.py                 # Weaviate schema building & data pipelining
│   │   ├── parser.py                   # Multi-engine Pydantic filter extraction
│   │   ├── prompts.py                  # Isolated system instruction matrices
│   │   ├── retriever.py                # Hybrid alpha-balanced vector routines
│   │   ├── security.py                 # Prompt injection & safety filters
│   │   └── validators.py               # Output factual correctness checkers
│   │
│   └── utils/
│       └── init_db.py                  # SQLite vault initializing routines
│
├── tests/
│   ├── dataset_creator.py              # LangSmith unit testing generator
│   ├── evaluation.py                   # Metric-normalization evaluators
│   ├── retrieval_eval.py               # Weaviate search stability test-harness
│   └── test_graph.py                   # Mock local terminal execution runner
│
├── nutricart_vault.db                  # Local SQLite secure profile store
├── main.py                             # Main FastAPI backend API server
└── .env                                # Infrastructure keys (Twilio, Google API)

```

---

## 🔧 Installation & Environment Setup

### 1. Prerequisite Infrastructure

Ensure you have local instances of Weaviate and Ollama running on your workstation:

* **Weaviate:** Running locally on `http://127.0.0.1:8080`.
* **Ollama:** Installed locally with the `llama3.2:3b` model pre-pulled:
```bash
ollama pull llama3.2:3b

```



### 2. Dependency Configuration

Clone the repository and install all required framework packages:

```bash
pip install fastapi uvicorn langgraph weaviate-client langchain-ollama langchain-google-genai aiosqlite pydantic python-dotenv langsmith

```

### 3. Environment Variables (`.env`)

Create an environment file in the workspace root directory:

```env
GOOGLE_API_KEY="your-gemini-cloud-key-here"
TWILIO_ACCOUNT_SID="your-twilio-sid-here"
TWILIO_AUTH_TOKEN="your-twilio-auth-token-here"

```

---

## 🚀 Execution & Verification Guide

### Step 1: Ingest Inventory and Embed Data

Execute the ingester pipeline to establish your localized Weaviate schema, normalize nutrient floats, and generate search embeddings:

```bash
python -m src.rag.ingester

```

### Step 2: Initialize SQLite Storage & Start FastAPI API Server

Launch the primary backend web process. The service uses modern lifespan context triggers to verify database structural keys automatically at boot:

```bash
python main.py

```

The API engine will spin up on **`http://127.0.0.1:8000`**.

### Step 3: Run the Local Terminal Test Harness

To run a test conversation through the graph nodes inside an isolated local console, launch `test_graph.py`:

```bash
python -m src.rag.test_graph

```

---

## 🧪 Evaluation & Testing Protocols

The platform maintains two continuous verification frameworks inside the system root folder:

### Phase 1: Retrieval Vector Benchmarking

Evaluates vector database stability and property exposure across the search index. It reads automated baseline constraint questions directly from `tests/dataset/queries.json` and evaluates search quality:

```bash
python -m tests.retrieval_eval

```

### Phase 2: LangSmith Unit Normalization Testing

Validates grammar-parsing capabilities (such as transforming raw query metrics like `mg` into standardized `g` scales). It streams testing pairs, tracks executions, and saves metrics inside the custom tracking identifier `"unit_normalization_score"`:

```bash
python -m tests.dataset_creator
python -m tests.evaluation

```

```
***

```