from collections.abc import AsyncGenerator

import anthropic

from app.config import settings

SYSTEM_PROMPT = (
    "You are Papyrus, an AI research assistant. You help researchers understand, "
    "compare, and synthesize academic papers.\n\n"
    "When answering questions, cite your sources using [Paper Title, p.X] format "
    "based on the provided context.\n"
    "If the provided context does not contain enough information to answer "
    "confidently, say so clearly rather than speculating.\n"
    "When generating literature review snippets, use formal academic prose "
    "and include proper in-text citations."
)

COMPARISON_ADDENDUM = (
    "\n\nThe user wants to compare aspects across multiple papers. Structure your "
    "response to address each paper and highlight similarities and differences. "
    "Use clear headings or sections for each paper when appropriate."
)

LITERATURE_REVIEW_ADDENDUM = (
    "\n\nThe user wants a literature review snippet. Write in formal academic prose "
    "with proper in-text citations (Author, Year) format. Synthesize the information "
    "across papers rather than summarizing each separately. Identify themes, "
    "agreements, disagreements, and gaps in the literature."
)


async def stream_response(
    user_message: str,
    context: str,
    conversation_history: list[dict] | None = None,
    mode: str = "default",
) -> AsyncGenerator[str]:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    system = SYSTEM_PROMPT
    if mode == "compare":
        system += COMPARISON_ADDENDUM
    elif mode == "literature_review":
        system += LITERATURE_REVIEW_ADDENDUM

    messages = []
    if conversation_history:
        messages.extend(conversation_history)

    prompt = f"""Here is relevant context from research papers:

{context}

---

User question: {user_message}"""

    messages.append({"role": "user", "content": prompt})

    async with client.messages.stream(
        model=settings.claude_model,
        max_tokens=4096,
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
