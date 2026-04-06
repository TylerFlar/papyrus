import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    citing_paper_id: Mapped[str] = mapped_column(String(36), ForeignKey("papers.id", ondelete="CASCADE"))
    cited_title: Mapped[str] = mapped_column(Text)
    cited_authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    cited_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cited_paper_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("papers.id", ondelete="SET NULL"), nullable=True
    )
    doi: Mapped[str | None] = mapped_column(String(500), nullable=True)
