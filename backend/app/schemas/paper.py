from datetime import datetime

from pydantic import BaseModel


class PaperResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str
    authors: str | None
    abstract: str | None
    filename: str
    page_count: int
    chunk_count: int
    status: str
    error_message: str | None
    uploaded_at: datetime
    processed_at: datetime | None


class PaperStatusResponse(BaseModel):
    id: str
    status: str
    chunk_count: int
    error_message: str | None
