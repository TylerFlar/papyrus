import logging
from datetime import datetime

from sqlalchemy import select

from app.database import async_session
from app.models.paper import Paper
from app.services.chunker import chunk_pages
from app.services.embeddings import embedding_service
from app.services.pdf_processor import extract_paper
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


async def process_paper(paper_id: str) -> None:
    async with async_session() as db:
        result = await db.execute(select(Paper).where(Paper.id == paper_id))
        paper = result.scalar_one_or_none()
        if not paper:
            logger.error("Paper %s not found", paper_id)
            return

        try:
            paper.status = "processing"
            await db.commit()

            logger.info("Extracting text from %s", paper.filename)
            extracted = extract_paper(paper.file_path)

            paper.title = extracted.metadata.title
            paper.authors = extracted.metadata.authors
            paper.abstract = extracted.metadata.abstract
            paper.page_count = extracted.metadata.page_count
            await db.commit()

            logger.info("Chunking %d pages", len(extracted.pages))
            chunks = chunk_pages(extracted.pages)

            if not chunks:
                paper.status = "error"
                paper.error_message = "No text could be extracted from the PDF"
                await db.commit()
                return

            logger.info("Embedding %d chunks", len(chunks))
            texts = [c.text for c in chunks]
            embeddings = embedding_service.embed_texts(texts)

            logger.info("Storing in vector DB")
            metadatas = [
                {
                    "chunk_index": c.chunk_index,
                    "page_number": c.page_number,
                    "section": c.section,
                }
                for c in chunks
            ]
            await vector_store.upsert_chunks(
                paper_id=paper.id,
                paper_title=paper.title,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            paper.chunk_count = len(chunks)
            paper.status = "ready"
            paper.processed_at = datetime.utcnow()
            await db.commit()
            logger.info("Paper %s processed successfully (%d chunks)", paper_id, len(chunks))

            # Extract citations as a post-processing step (non-blocking)
            try:
                from app.services.citation_extractor import process_citations

                cite_count = await process_citations(paper.id, extracted.full_text, db)
                logger.info("Extracted %d citations for paper %s", cite_count, paper_id)
            except Exception as cite_err:
                logger.warning("Citation extraction failed for %s: %s", paper_id, cite_err)

        except Exception as e:
            logger.exception("Error processing paper %s", paper_id)
            paper.status = "error"
            paper.error_message = str(e)[:1000]
            await db.commit()
