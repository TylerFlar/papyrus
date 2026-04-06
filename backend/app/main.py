from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models.citation  # noqa: F401
import app.models.conversation  # noqa: F401
import app.models.paper  # noqa: F401 — register models before create_all
from app.config import settings
from app.database import init_db
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    embedding_service.load_model()
    await vector_store.ensure_collection()
    yield


app = FastAPI(title="Papyrus", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import chat, citations, health, papers  # noqa: E402

app.include_router(health.router, prefix="/api")
app.include_router(papers.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(citations.router, prefix="/api")
