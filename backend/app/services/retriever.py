from collections import defaultdict

from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store


async def retrieve_chunks(
    query: str,
    paper_ids: list[str] | None = None,
    section: str | None = None,
    top_k: int = 10,
    max_chunks: int = 5,
    score_threshold: float = 0.2,
) -> list[dict]:
    query_vector = embedding_service.embed_query(query)
    results = await vector_store.search(
        query_vector=query_vector,
        paper_ids=paper_ids,
        limit=top_k,
        score_threshold=score_threshold,
    )

    if section:
        section_lower = section.lower()
        results = [
            r for r in results if r.get("section", "").lower() == section_lower
        ] or results  # fall back to unfiltered if no section matches

    return results[:max_chunks]


async def retrieve_chunks_grouped(
    query: str,
    paper_ids: list[str],
    section: str | None = None,
    chunks_per_paper: int = 3,
    score_threshold: float = 0.2,
) -> dict[str, list[dict]]:
    """Retrieve chunks grouped by paper for multi-paper comparison."""
    query_vector = embedding_service.embed_query(query)

    # Retrieve more to ensure coverage across all papers
    results = await vector_store.search(
        query_vector=query_vector,
        paper_ids=paper_ids,
        limit=chunks_per_paper * len(paper_ids) * 2,
        score_threshold=score_threshold,
    )

    if section:
        section_lower = section.lower()
        filtered = [r for r in results if r.get("section", "").lower() == section_lower]
        if filtered:
            results = filtered

    # Group by paper
    grouped: dict[str, list[dict]] = defaultdict(list)
    for chunk in results:
        pid = chunk.get("paper_id", "")
        if len(grouped[pid]) < chunks_per_paper:
            grouped[pid].append(chunk)

    return dict(grouped)


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        title = chunk.get("paper_title", "Unknown")
        page = chunk.get("page_number", "?")
        section = chunk.get("section")
        text = chunk.get("text", "")
        header = f"[Source {i}: {title}, p.{page}"
        if section:
            header += f", {section}"
        header += "]"
        parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(parts)


def format_grouped_context(grouped: dict[str, list[dict]]) -> str:
    if not grouped:
        return "No relevant context found."

    parts = []
    for _paper_id, chunks in grouped.items():
        if not chunks:
            continue
        title = chunks[0].get("paper_title", "Unknown")
        paper_parts = [f"## From: {title}"]
        for chunk in chunks:
            page = chunk.get("page_number", "?")
            section = chunk.get("section")
            text = chunk.get("text", "")
            header = f"[p.{page}"
            if section:
                header += f", {section}"
            header += "]"
            paper_parts.append(f"{header}\n{text}")
        parts.append("\n\n".join(paper_parts))

    return "\n\n===\n\n".join(parts)
