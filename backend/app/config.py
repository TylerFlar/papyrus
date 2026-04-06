from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    anthropic_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "sqlite+aiosqlite:///./papyrus.db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    claude_model: str = "claude-sonnet-4-20250514"
    upload_dir: str = "./uploads"
    cors_origins: str = "http://localhost:3000"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
