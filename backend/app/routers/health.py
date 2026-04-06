from fastapi import APIRouter

from app.services.vector_store import vector_store

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    qdrant_ok = await vector_store.health_check()
    return {
        "status": "healthy" if qdrant_ok else "degraded",
        "qdrant": "connected" if qdrant_ok else "disconnected",
    }
