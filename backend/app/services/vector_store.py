import logging
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.services.embeddings import embedding_service

logger = logging.getLogger(__name__)

COLLECTION_NAME = "paper_chunks"


class VectorStore:
    def __init__(self) -> None:
        self.client = AsyncQdrantClient(url=settings.qdrant_url)

    async def ensure_collection(self) -> None:
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]
        if COLLECTION_NAME not in names:
            logger.info("Creating Qdrant collection: %s", COLLECTION_NAME)
            await self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=embedding_service.dimension,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_chunks(
        self,
        paper_id: str,
        paper_title: str,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        points = [
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{paper_id}_{i}")),
                vector=embedding,
                payload={
                    "paper_id": paper_id,
                    "paper_title": paper_title,
                    "text": text,
                    **meta,
                },
            )
            for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadatas, strict=True))
        ]
        batch_size = 100
        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            await self.client.upsert(collection_name=COLLECTION_NAME, points=batch)
        logger.info("Upserted %d chunks for paper %s", len(points), paper_id)

    async def delete_by_paper_id(self, paper_id: str) -> None:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        await self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(must=[FieldCondition(key="paper_id", match=MatchValue(value=paper_id))]),
        )

    async def search(
        self,
        query_vector: list[float],
        paper_ids: list[str] | None = None,
        limit: int = 10,
        score_threshold: float = 0.2,
    ) -> list[dict]:
        from qdrant_client.models import FieldCondition, Filter, MatchAny

        query_filter = None
        if paper_ids:
            query_filter = Filter(must=[FieldCondition(key="paper_id", match=MatchAny(any=paper_ids))])

        results = await self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return [
            {
                "score": point.score,
                **point.payload,
            }
            for point in results.points
        ]

    async def health_check(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False


vector_store = VectorStore()
