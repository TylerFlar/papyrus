from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.conversation import Conversation, ConversationPaper, Message
from app.schemas.chat import (
    ConversationListItem,
    ConversationResponse,
    CreateConversationRequest,
    MessageResponse,
    SendMessageRequest,
)
from app.services.chat_service import process_message

router = APIRouter(tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    req: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(title=req.title)
    db.add(conv)
    await db.flush()

    for paper_id in req.paper_ids:
        db.add(ConversationPaper(conversation_id=conv.id, paper_id=paper_id))

    await db.commit()
    await db.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        paper_ids=req.paper_ids,
        messages=[],
    )


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).order_by(Conversation.updated_at.desc()))
    conversations = result.scalars().all()

    items = []
    for conv in conversations:
        paper_result = await db.execute(
            select(ConversationPaper.paper_id).where(ConversationPaper.conversation_id == conv.id)
        )
        paper_ids = list(paper_result.scalars().all())
        items.append(
            ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                paper_ids=paper_ids,
            )
        )
    return items


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    paper_result = await db.execute(
        select(ConversationPaper.paper_id).where(ConversationPaper.conversation_id == conversation_id)
    )
    paper_ids = list(paper_result.scalars().all())

    msg_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    )
    messages = [MessageResponse.model_validate(m) for m in msg_result.scalars().all()]

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        paper_ids=paper_ids,
        messages=messages,
    )


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    return StreamingResponse(
        process_message(
            db=db,
            conversation_id=conversation_id,
            user_message=req.message,
            paper_ids=req.paper_ids,
            mode=req.mode,
            section=req.section,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete messages and paper associations
    msg_result = await db.execute(select(Message).where(Message.conversation_id == conversation_id))
    for msg in msg_result.scalars().all():
        await db.delete(msg)

    cp_result = await db.execute(select(ConversationPaper).where(ConversationPaper.conversation_id == conversation_id))
    for cp in cp_result.scalars().all():
        await db.delete(cp)

    await db.delete(conv)
    await db.commit()
    return {"detail": "Conversation deleted"}
