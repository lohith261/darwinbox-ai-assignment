# Darwinbox Agentic HR Workflow Engine

Production-ready scaffold for an AI Engineering assignment built with FastAPI, Streamlit, LangGraph, LangChain, ChromaDB, OpenAI, SQLite, and Python 3.12.

## Project Structure

```text
.
├── backend/
│   ├── agents/
│   ├── api/
│   ├── config/
│   ├── core/
│   ├── memory/
│   ├── rag/
│   ├── schemas/
│   ├── services/
│   ├── tools/
│   ├── tracing/
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── chroma/
│   ├── sqlite/
│   └── .gitkeep
├── docs/
│   ├── architecture.md
│   └── hr_policy.md
├── frontend/
│   ├── __init__.py
│   └── app.py
├── tests/
│   ├── test_health.py
│   └── test_workflow.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Local Setup

1. Create an environment file:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Ingest the HR policy corpus into ChromaDB:

   ```bash
   uv run python -m backend.rag.ingest
   ```

4. Start the API:

   ```bash
   uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Start the Streamlit frontend in a separate terminal:

   ```bash
   uv run streamlit run frontend/app.py
   ```

## Quality Checks

Run the full local quality suite:

```bash
uv run ruff check .
uv run black --check .
uv run mypy backend frontend tests
uv run pytest
```

## Workflow Endpoints

- `GET /health`
- `POST /api/v1/workflows/invoke`
- `GET /api/v1/workflows/graph`
- `GET /api/v1/workflows/sessions/{session_id}`

## Policy Retrieval

- The source policy corpus is [docs/hr_policy.md](/Users/bandreddysrisailohith/Desktop/Darwin/docs/hr_policy.md).
- Ingestion loads the markdown policy, chunks it, generates OpenAI embeddings, and stores vectors in ChromaDB under `data/chroma/`.
- `PolicyAgent` answers only from retrieved policy chunks. If no supporting context is retrieved, it returns a clear `Policy unavailable` response instead of guessing.

## Docker

Build and run both services:

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:8501`

## Key Features Implemented

- **Deterministic Routing Optimization**: Automatically detects simple queries (leave balances, payslip downloads, leave application) and routes directly to the Action Agent, bypassing LLM calls to reduce token costs by at least 20%.
- **Production Observability**: The `TraceManager` records request timestamps, executed agents, tool metrics, API retries/failures, token counts, and costs, exporting JSON traces to `data/traces/`.
- **Conversation Memory**: Persists conversation context (e.g. Employee ID, selected leave dates, tool outputs) dynamically across turns using LangGraph checkpointers.
- **Resilient Mock APIs**: Simulates network latency, timeouts (0.8s), retries (up to 2), and fallback caches for leaf balances, leave applications, and payslip retrievals.
- **Offline Fallbacks**: Automatically falls back to `DummyEmbeddings` if OpenAI API keys are unconfigured, enabling local testing.

