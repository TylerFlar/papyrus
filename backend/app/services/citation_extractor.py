import json
import logging
import re
from difflib import SequenceMatcher

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.citation import Citation
from app.models.paper import Paper

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
Extract all references/citations from the following bibliography/references section.
Return a JSON array where each element has:
- "title": the title of the cited work (string)
- "authors": the authors (string or null)
- "year": the publication year (integer or null)
- "doi": the DOI if present (string or null)

Only return the JSON array, nothing else. If no references are found, return an empty array [].

References text:
"""


def extract_references_section(full_text: str) -> str | None:
    """Find the references/bibliography section at the end of the paper."""
    text_lower = full_text.lower()

    # Look for references section header
    markers = ["references", "bibliography", "works cited", "literature cited"]
    best_start = -1

    for marker in markers:
        # Search from the back of the document (references are typically at the end)
        idx = text_lower.rfind(marker)
        if idx != -1 and idx > len(full_text) * 0.5 and (best_start == -1 or idx > best_start):
            best_start = idx

    if best_start == -1:
        return None

    # Skip the heading line
    newline_idx = full_text.find("\n", best_start)
    if newline_idx != -1:
        best_start = newline_idx + 1

    references_text = full_text[best_start:].strip()
    # Cap at 10000 chars to avoid huge context
    return references_text[:10000] if references_text else None


async def extract_citations_from_text(references_text: str) -> list[dict]:
    """Use Claude to extract structured citations from references text."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=4096,
            messages=[{"role": "user", "content": EXTRACTION_PROMPT + references_text}],
        )
        content = response.content[0].text.strip()

        # Try to extract JSON from the response
        # Handle cases where Claude wraps in ```json blocks
        if "```" in content:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()

        citations = json.loads(content)
        if not isinstance(citations, list):
            return []
        return citations
    except Exception as e:
        logger.error("Failed to extract citations: %s", e)
        return []


def fuzzy_match_title(title1: str, title2: str, threshold: float = 0.85) -> bool:
    """Check if two titles are similar enough to be the same work."""
    t1 = re.sub(r"[^\w\s]", "", title1.lower()).strip()
    t2 = re.sub(r"[^\w\s]", "", title2.lower()).strip()
    return SequenceMatcher(None, t1, t2).ratio() >= threshold


async def process_citations(paper_id: str, full_text: str, db: AsyncSession) -> int:
    """Extract citations from a paper and store them, returning count of citations found."""
    refs_text = extract_references_section(full_text)
    if not refs_text:
        logger.info("No references section found for paper %s", paper_id)
        return 0

    raw_citations = await extract_citations_from_text(refs_text)
    if not raw_citations:
        return 0

    # Get all uploaded papers for cross-matching
    result = await db.execute(select(Paper).where(Paper.status == "ready"))
    uploaded_papers = {p.id: p for p in result.scalars().all()}

    count = 0
    for cite_data in raw_citations:
        title = cite_data.get("title", "").strip()
        if not title:
            continue

        # Try to match against uploaded papers
        matched_paper_id = None
        for pid, paper in uploaded_papers.items():
            if pid == paper_id:
                continue
            if fuzzy_match_title(title, paper.title):
                matched_paper_id = pid
                break

        citation = Citation(
            citing_paper_id=paper_id,
            cited_title=title,
            cited_authors=cite_data.get("authors"),
            cited_year=cite_data.get("year"),
            cited_paper_id=matched_paper_id,
            doi=cite_data.get("doi"),
        )
        db.add(citation)
        count += 1

    await db.commit()
    logger.info("Extracted %d citations for paper %s", count, paper_id)
    return count
