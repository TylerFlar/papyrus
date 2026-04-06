from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.citation import Citation
from app.models.paper import Paper
from app.schemas.citation import (
    CitationGraphResponse,
    CitationResponse,
    GraphEdge,
    GraphNode,
)

router = APIRouter(tags=["citations"])


@router.get("/citations/graph", response_model=CitationGraphResponse)
async def get_citation_graph(db: AsyncSession = Depends(get_db)):
    # Get all uploaded papers
    paper_result = await db.execute(select(Paper).where(Paper.status == "ready"))
    papers = {p.id: p for p in paper_result.scalars().all()}

    # Get all citations
    cite_result = await db.execute(select(Citation))
    citations = cite_result.scalars().all()

    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []
    citation_counts: dict[str, int] = defaultdict(int)

    # Add uploaded papers as nodes
    for pid, paper in papers.items():
        nodes[pid] = GraphNode(
            id=pid,
            title=paper.title,
            is_uploaded=True,
        )

    # Process citations
    for cite in citations:
        if cite.cited_paper_id and cite.cited_paper_id in papers:
            # Citation links to an uploaded paper
            target_id = cite.cited_paper_id
            citation_counts[target_id] += 1
            edges.append(GraphEdge(source=cite.citing_paper_id, target=target_id))
        else:
            # External citation — create a node for it
            # Use a deterministic ID based on the title for deduplication
            ext_id = f"ext:{cite.cited_title[:100].lower().strip()}"
            if ext_id not in nodes:
                nodes[ext_id] = GraphNode(
                    id=ext_id,
                    title=cite.cited_title,
                    is_uploaded=False,
                )
            citation_counts[ext_id] += 1
            edges.append(GraphEdge(source=cite.citing_paper_id, target=ext_id))

    # Update citation counts
    for node_id, count in citation_counts.items():
        if node_id in nodes:
            nodes[node_id].citation_count = count

    return CitationGraphResponse(
        nodes=list(nodes.values()),
        edges=edges,
    )


@router.get("/papers/{paper_id}/citations", response_model=list[CitationResponse])
async def get_paper_citations(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Citation).where(Citation.citing_paper_id == paper_id))
    return result.scalars().all()
