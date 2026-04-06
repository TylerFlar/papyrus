from pydantic import BaseModel


class CitationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    citing_paper_id: str
    cited_title: str
    cited_authors: str | None
    cited_year: int | None
    cited_paper_id: str | None
    doi: str | None


class GraphNode(BaseModel):
    id: str
    title: str
    is_uploaded: bool
    citation_count: int = 0


class GraphEdge(BaseModel):
    source: str
    target: str


class CitationGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
