from datetime import datetime

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    paper_ids: list[str]
    title: str | None = None


class SendMessageRequest(BaseModel):
    message: str
    paper_ids: list[str] | None = None
    mode: str = "default"  # "default" | "compare" | "literature_review"
    section: str | None = None  # filter retrieval to specific section


class MessageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    conversation_id: str
    role: str
    content: str
    sources: str | None
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime
    paper_ids: list[str] = []
    messages: list[MessageResponse] = []


class ConversationListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime
    paper_ids: list[str] = []
