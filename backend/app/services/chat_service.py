import json
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, ConversationPaper, Message
from app.services.llm import stream_response
from app.services.retriever import (
    format_context,
    format_grouped_context,
    retrieve_chunks,
    retrieve_chunks_grouped,
)


async def get_conversation_history(db: AsyncSession, conversation_id: str, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content} for m in messages]


async def get_conversation_paper_ids(db: AsyncSession, conversation_id: str) -> list[str]:
    result = await db.execute(
        select(ConversationPaper.paper_id).where(ConversationPaper.conversation_id == conversation_id)
    )
    return list(result.scalars().all())


async def process_message(
    db: AsyncSession,
    conversation_id: str,
    user_message: str,
    paper_ids: list[str] | None = None,
    mode: str = "default",
    section: str | None = None,
) -> AsyncGenerator[str]:
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    await db.commit()

    # Get paper scope
    if paper_ids is None:
        paper_ids = await get_conversation_paper_ids(db, conversation_id)

    # Determine if this is a multi-paper comparison
    use_compare = mode in ("compare", "literature_review") and paper_ids and len(paper_ids) > 1

    # Retrieve relevant chunks
    all_chunks: list[dict] = []
    if use_compare:
        grouped = await retrieve_chunks_grouped(
            query=user_message,
            paper_ids=paper_ids,
            section=section,
        )
        context = format_grouped_context(grouped)
        for chunks in grouped.values():
            all_chunks.extend(chunks)
    else:
        all_chunks = await retrieve_chunks(
            query=user_message,
            paper_ids=paper_ids if paper_ids else None,
            section=section,
        )
        context = format_context(all_chunks)

    # Send sources event
    sources_data = [
        {
            "paper_id": c.get("paper_id"),
            "paper_title": c.get("paper_title"),
            "page_number": c.get("page_number"),
            "chunk_index": c.get("chunk_index"),
            "section": c.get("section"),
            "score": c.get("score"),
        }
        for c in all_chunks
    ]
    yield f"event: sources\ndata: {json.dumps({'sources': sources_data})}\n\n"

    # Get conversation history
    history = await get_conversation_history(db, conversation_id)
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    # Stream response
    full_response = ""
    async for token in stream_response(
        user_message=user_message,
        context=context,
        conversation_history=history if history else None,
        mode=mode,
    ):
        full_response += token
        yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=full_response,
        sources=json.dumps(sources_data),
    )
    db.add(assistant_msg)

    # Update conversation title if first exchange
    conv_result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = conv_result.scalar_one_or_none()
    if conv and not conv.title:
        conv.title = user_message[:100]

    await db.commit()

    yield f"event: done\ndata: {json.dumps({})}\n\n"
