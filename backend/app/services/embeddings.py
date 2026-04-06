import logging

from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self.model: SentenceTransformer | None = None

    def load_model(self) -> None:
        logger.info("Loading embedding model: %s", settings.embedding_model)
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded (dim=%d)", self.model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


embedding_service = EmbeddingService()
