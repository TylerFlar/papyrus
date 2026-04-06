from dataclasses import dataclass, field
from pathlib import Path

import pymupdf


@dataclass
class PaperMetadata:
    title: str = "Untitled"
    authors: str | None = None
    abstract: str | None = None
    page_count: int = 0


@dataclass
class ExtractedPaper:
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    pages: list[str] = field(default_factory=list)
    full_text: str = ""


def extract_paper(file_path: str | Path) -> ExtractedPaper:
    doc = pymupdf.open(str(file_path))
    pages: list[str] = []

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text)

    full_text = "\n\n".join(pages)
    metadata = _extract_metadata(doc, full_text)
    metadata.page_count = len(doc)
    doc.close()

    return ExtractedPaper(metadata=metadata, pages=pages, full_text=full_text)


def _extract_metadata(doc: pymupdf.Document, full_text: str) -> PaperMetadata:
    meta = doc.metadata or {}
    title = meta.get("title", "").strip()
    author = meta.get("author", "").strip()

    if not title:
        lines = full_text.strip().split("\n")
        for line in lines[:10]:
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith("http"):
                title = stripped[:500]
                break

    abstract = _extract_abstract(full_text)

    return PaperMetadata(
        title=title or "Untitled",
        authors=author or None,
        abstract=abstract,
    )


def _extract_abstract(text: str) -> str | None:
    text_lower = text.lower()
    start_markers = ["abstract", "summary"]
    end_markers = ["introduction", "1.", "1 ", "keywords", "key words"]

    for marker in start_markers:
        idx = text_lower.find(marker)
        if idx == -1:
            continue

        start = idx + len(marker)
        while start < len(text) and text[start] in ("\n", " ", ".", ":", "-"):
            start += 1

        chunk = text[start : start + 3000]
        best_end = len(chunk)

        for end_marker in end_markers:
            end_idx = chunk.lower().find(end_marker)
            if end_idx > 50:
                best_end = min(best_end, end_idx)

        abstract = chunk[:best_end].strip()
        if len(abstract) > 50:
            return abstract

    return None
