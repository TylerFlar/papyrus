# Papyrus

AI-powered research assistant that lets you upload academic papers (PDFs) and chat with them using retrieval-augmented generation (RAG). Ask questions, get summaries, compare methodologies across papers, generate literature review snippets, and visualize citation networks.

## Features

- **PDF Upload & Processing** — Upload research papers; they're automatically parsed, chunked, and embedded
- **Chat with Papers** — Ask questions and get cited, streaming responses powered by Claude
- **Multi-Paper Comparison** — Select multiple papers and compare methodologies, findings, or generate comparative reviews
- **Section-Aware Retrieval** — Filter queries to specific paper sections (Methods, Results, Discussion, etc.)
- **Literature Review Generation** — Generate formal academic prose synthesizing information across papers
- **Citation Graph** — Interactive force-directed visualization of citation relationships between papers

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.12, SQLAlchemy (async), Pydantic |
| Vector DB | Qdrant |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2, local) |
| LLM | Claude API (Anthropic) |
| Graph Viz | react-force-graph-2d |

## Project Structure

```
papyrus/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry, CORS, lifespan
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # Async SQLAlchemy + SQLite
│   │   ├── routers/             # papers, chat, citations, health
│   │   ├── services/            # pdf_processor, chunker, embeddings,
│   │   │                        # vector_store, retriever, llm,
│   │   │                        # chat_service, citation_extractor
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── tasks/               # Background processing pipeline
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Pages: /, /upload, /library,
│   │   │                        #   /chat, /chat/[id], /graph
│   │   ├── components/          # chat/, papers/, graph/, layout/
│   │   ├── hooks/               # usePapers, useChat
│   │   ├── lib/                 # API client, utils
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 22+ and pnpm
- Docker (for Qdrant)
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
# Clone the repo
git clone git@github.com:TylerFlar/papyrus.git
cd papyrus

# Copy environment config
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Option A: Docker Compose (recommended)

```bash
docker compose up
```

This starts Qdrant (`:6333`), the backend (`:8000`), and the frontend (`:3000`).

### Option B: Run individually

```bash
# 1. Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant:v1.13.2

# 2. Start the backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# 3. Start the frontend (in another terminal)
cd frontend
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Your Anthropic API key (required) |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `DATABASE_URL` | `sqlite+aiosqlite:///./papyrus.db` | Database connection string |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model name |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model for generation |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded PDFs |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |

## API Endpoints

### Papers
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/papers/upload` | Upload a PDF (multipart form) |
| `GET` | `/api/papers` | List all papers |
| `GET` | `/api/papers/{id}` | Get paper details |
| `GET` | `/api/papers/{id}/status` | Poll processing status |
| `DELETE` | `/api/papers/{id}` | Delete paper and its vectors |

### Chat
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/{id}` | Get conversation with messages |
| `POST` | `/api/conversations/{id}/messages` | Send message (returns SSE stream) |
| `DELETE` | `/api/conversations/{id}` | Delete conversation |

### Citations
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/citations/graph` | Citation graph (nodes + edges) |
| `GET` | `/api/papers/{id}/citations` | Citations for a paper |

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check + Qdrant status |

## Development

### Backend

```bash
cd backend

# Install dependencies (including dev)
uv sync --dev

# Run linter
uv run ruff check .

# Run formatter check
uv run ruff format --check .

# Auto-fix lint issues
uv run ruff check --fix .

# Auto-format
uv run ruff format .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest -v
```

### Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Run linter
pnpm lint

# Type check
pnpm type-check

# Build
pnpm build

# Dev server
pnpm dev
```

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Browser    │     │            Backend (FastAPI)          │
│  (Next.js)   │────▶│                                      │
│              │ SSE │  ┌──────────┐  ┌───────────────────┐ │
│  /upload     │◀────│  │ Routers  │  │    Services        │ │
│  /library    │     │  │  papers  │──│  pdf_processor     │ │
│  /chat       │     │  │  chat    │  │  chunker           │ │
│  /graph      │     │  │  citations│  │  embeddings        │ │
│              │     │  │  health  │  │  vector_store      │ │
└─────────────┘     │  └──────────┘  │  retriever         │ │
                    │                │  llm (Claude API)   │ │
                    │                │  chat_service       │ │
                    │                │  citation_extractor │ │
                    │                └───────────────────┘ │
                    │                        │     │       │
                    │                   ┌────▼─┐ ┌─▼────┐  │
                    │                   │SQLite│ │Qdrant│  │
                    │                   └──────┘ └──────┘  │
                    └──────────────────────────────────────┘
```

## License

MIT
