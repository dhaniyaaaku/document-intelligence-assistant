# Document Intelligence Assistant

Production-quality RAG + agentic AI application. Upload PDFs, DOCX, or TXT files
and ask natural-language questions about them. A LangGraph agent picks the right
tool (search, summarize, extract topics, compare, action items, QA) for each
request, and answers are grounded in the source documents with inline citations.

## Stack

| Layer            | Technology                                |
|------------------|-------------------------------------------|
| API backend      | FastAPI + Uvicorn                         |
| LLM              | Google Gemini 2.0 Flash via LangChain     |
| Agent            | LangGraph (`create_react_agent`)          |
| Embeddings       | `sentence-transformers/all-MiniLM-L6-v2`  |
| Vector store     | ChromaDB (persistent)                     |
| Metadata DB      | SQLite via SQLAlchemy                     |
| Frontend         | Streamlit                                 |
| Container        | Docker + docker-compose                   |
| CI               | GitHub Actions (lint, test, image build)  |

## Architecture

```
Streamlit  ──HTTP──>  FastAPI  ──>  Services  ──>  RAG (Chroma + embeddings)
                                       │
                                       └──>  LangGraph agent ──> tools ──> services
```

* **`backend/api/`** — FastAPI routers (`documents`, `chat`, `analysis`).
* **`backend/services/`** — Use-case orchestration (document, chat, analysis, LLM client).
* **`backend/agents/`** — LangGraph ReAct agent and its tool wrappers.
* **`backend/rag/`** — Extraction, chunking, embeddings, vector store.
* **`backend/database/`** — SQLAlchemy models and session factory.
* **`backend/models/`** — Pydantic request/response schemas.
* **`backend/utils/`** — Config (pydantic-settings) and logging.
* **`frontend/`** — Streamlit dashboard (chat, summary, comparison, insights tabs).
* **`docker/`** — Backend and frontend Dockerfiles.
* **`.github/workflows/`** — CI: lint, tests, image build.
* **`tests/`** — pytest suite.

## Quick start (Docker — recommended)

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY (see below)
docker compose up --build
```

Then open:

* Streamlit UI: <http://localhost:8501>
* FastAPI docs: <http://localhost:8000/docs>

## Quick start (local Python)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env            # then edit and add GEMINI_API_KEY

# Terminal 1 — backend
uvicorn backend.main:app --reload

# Terminal 2 — frontend
streamlit run frontend/streamlit_app.py
```

## Getting a Gemini API key (free tier)

1. Go to <https://aistudio.google.com/app/apikey>.
2. Sign in with a Google account.
3. Click **Create API key** → copy the key.
4. Paste it into `.env` as `GEMINI_API_KEY=...`.

The free tier of `gemini-2.0-flash` is generous enough for portfolio demos.

## API surface

| Method | Path                       | Purpose                                          |
|--------|----------------------------|--------------------------------------------------|
| GET    | `/health`                  | Liveness check                                   |
| POST   | `/documents/upload`        | Upload + index a PDF/DOCX/TXT                    |
| GET    | `/documents`               | List indexed documents                           |
| DELETE | `/documents/{id}`          | Delete a document and its embeddings             |
| POST   | `/chat`                    | Plain RAG QA                                     |
| POST   | `/chat/agent`              | LangGraph agent (auto-picks the right tool)      |
| POST   | `/analysis/summarize`      | Summarize a document                             |
| POST   | `/analysis/topics`         | Extract top-N topics                             |
| POST   | `/analysis/compare`        | Compare two documents                            |
| POST   | `/analysis/action-items`   | Extract action items                             |

## Tests

```bash
pytest -q
```

The upload roundtrip test downloads the embedding model on first run; it
auto-skips in environments without network access.

## CI

`.github/workflows/ci.yml` runs on every push and PR to `main`:

1. Install dependencies
2. `ruff check`
3. `pytest`
4. Build both Docker images

## Anti-hallucination design

* The chat service uses a strict system prompt that forbids answering outside
  the retrieved context and tells the model to say *"I cannot find this in the
  uploaded documents"* when context is insufficient.
* Every answer ships with the source chunks it used, surfaced in the UI under
  an expandable **Sources** panel.
* The agent surfaces its tool call and a redacted trace under **Agent trace**.

## License

MIT.
