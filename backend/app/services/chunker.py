import re
from dataclasses import dataclass

from app.config import settings

SEPARATORS = ["\n\n", "\n", ". ", " "]

SECTION_PATTERNS = [
    re.compile(r"^(abstract)\b", re.IGNORECASE),
    re.compile(r"^(introduction)\b", re.IGNORECASE),
    re.compile(r"^(background)\b", re.IGNORECASE),
    re.compile(r"^(related\s+work)\b", re.IGNORECASE),
    re.compile(r"^(literature\s+review)\b", re.IGNORECASE),
    re.compile(r"^(methods?|methodology)\b", re.IGNORECASE),
    re.compile(r"^(materials?\s+and\s+methods?)\b", re.IGNORECASE),
    re.compile(r"^(experimental?\s+(?:setup|design))\b", re.IGNORECASE),
    re.compile(r"^(results?)\b", re.IGNORECASE),
    re.compile(r"^(results?\s+and\s+discussion)\b", re.IGNORECASE),
    re.compile(r"^(discussion)\b", re.IGNORECASE),
    re.compile(r"^(conclusion|conclusions|concluding\s+remarks)\b", re.IGNORECASE),
    re.compile(r"^(references|bibliography)\b", re.IGNORECASE),
    re.compile(r"^(appendix|appendices)\b", re.IGNORECASE),
    # Numbered sections like "1. Introduction", "2 Methods"
    re.compile(
        r"^\d+\.?\s+(introduction|background|methods?|methodology|results?|discussion|conclusion)", re.IGNORECASE
    ),
]


@dataclass
class Chunk:
    text: str
    chunk_index: int
    page_number: int | None = None
    section: str | None = None


def detect_section(text: str) -> str | None:
    for line in text.split("\n")[:3]:
        line = line.strip()
        if not line or len(line) > 100:
            continue
        for pattern in SECTION_PATTERNS:
            match = pattern.match(line)
            if match:
                # Normalize section name
                raw = match.group(1) if match.lastindex else match.group(0)
                return _normalize_section(raw)
    return None


def _normalize_section(raw: str) -> str:
    raw = re.sub(r"^\d+\.?\s*", "", raw).strip().lower()
    mapping = {
        "abstract": "Abstract",
        "introduction": "Introduction",
        "background": "Background",
        "related work": "Related Work",
        "literature review": "Literature Review",
        "method": "Methods",
        "methods": "Methods",
        "methodology": "Methods",
        "materials and methods": "Methods",
        "materials and method": "Methods",
        "material and methods": "Methods",
        "experimental setup": "Methods",
        "experimental design": "Methods",
        "experiment setup": "Methods",
        "result": "Results",
        "results": "Results",
        "results and discussion": "Results and Discussion",
        "result and discussion": "Results and Discussion",
        "discussion": "Discussion",
        "conclusion": "Conclusion",
        "conclusions": "Conclusion",
        "concluding remarks": "Conclusion",
        "references": "References",
        "bibliography": "References",
        "appendix": "Appendix",
        "appendices": "Appendix",
    }
    return mapping.get(raw, raw.title())


def chunk_text(
    text: str,
    chunk_size: int = settings.chunk_size,
    chunk_overlap: int = settings.chunk_overlap,
) -> list[Chunk]:
    raw_chunks = _recursive_split(text, chunk_size, chunk_overlap)
    return [Chunk(text=t, chunk_index=i, section=detect_section(t)) for i, t in enumerate(raw_chunks) if t.strip()]


def chunk_pages(
    pages: list[str],
    chunk_size: int = settings.chunk_size,
    chunk_overlap: int = settings.chunk_overlap,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0
    current_section: str | None = None

    for page_num, page_text in enumerate(pages, start=1):
        page_chunks = _recursive_split(page_text, chunk_size, chunk_overlap)
        for text in page_chunks:
            if not text.strip():
                continue
            detected = detect_section(text)
            if detected:
                current_section = detected
            chunks.append(
                Chunk(
                    text=text,
                    chunk_index=idx,
                    page_number=page_num,
                    section=current_section,
                )
            )
            idx += 1
    return chunks


def _recursive_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: list[str] | None = None,
) -> list[str]:
    if separators is None:
        separators = SEPARATORS

    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    separator = separators[-1]
    for sep in separators:
        if sep in text:
            separator = sep
            break

    splits = text.split(separator)
    chunks: list[str] = []
    current = ""

    for split in splits:
        piece = split if not current else separator + split
        if len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            if current.strip():
                chunks.append(current.strip())
            overlap_text = _get_overlap(current, chunk_overlap)
            current = overlap_text + piece if overlap_text else split

    if current.strip():
        chunks.append(current.strip())

    return chunks


def _get_overlap(text: str, overlap_size: int) -> str:
    if len(text) <= overlap_size:
        return text
    return text[-overlap_size:]
