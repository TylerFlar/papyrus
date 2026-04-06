import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.paper import Paper
from app.schemas.paper import PaperResponse, PaperStatusResponse
from app.services.vector_store import vector_store
from app.tasks.process_paper import process_paper

router = APIRouter(tags=["papers"])


@router.post("/papers/upload", response_model=PaperResponse)
async def upload_paper(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    paper_id = str(uuid.uuid4())
    file_path = settings.upload_path / f"{paper_id}.pdf"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    paper = Paper(
        id=paper_id,
        filename=file.filename,
        file_path=str(file_path),
        status="uploading",
    )
    db.add(paper)
    await db.commit()
    await db.refresh(paper)

    paper.status = "processing"
    await db.commit()

    background_tasks.add_task(process_paper, paper_id)

    return paper


@router.get("/papers", response_model=list[PaperResponse])
async def list_papers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).order_by(Paper.uploaded_at.desc()))
    return result.scalars().all()


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/papers/{paper_id}/status", response_model=PaperStatusResponse)
async def get_paper_status(paper_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/papers/{paper_id}")
async def delete_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    await vector_store.delete_by_paper_id(paper_id)

    import os

    if os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    await db.delete(paper)
    await db.commit()
    return {"detail": "Paper deleted"}
