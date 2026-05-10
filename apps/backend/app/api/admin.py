from __future__ import annotations

from pathlib import Path
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_token, get_db_session
from app.core.config import get_settings
from app.models.entities import IngestionJob
from app.schemas.admin import IngestionTriggerRequest, IngestionTriggerResponse
from app.scraper.dol_downloader import download_dataset
from app.services.ingestion_service import run_ingestion_job

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)
settings = get_settings()


async def _run_ingestion(dataset_year: int, dataset_url: str, session: AsyncSession) -> IngestionJob:
    data_dir = Path("data")
    dataset_path = await download_dataset(dataset_url, output_dir=data_dir)
    return await run_ingestion_job(
        session=session,
        dataset_year=dataset_year,
        source_url=dataset_url,
        dataset_path=dataset_path,
    )


@router.post("/ingestion/run", response_model=IngestionTriggerResponse, dependencies=[Depends(get_admin_token)])
async def trigger_ingestion(
    payload: IngestionTriggerRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> IngestionTriggerResponse:
    existing_running = (
        await session.execute(select(IngestionJob).where(IngestionJob.status == "running").limit(1))
    ).scalar_one_or_none()
    if existing_running:
        raise HTTPException(status_code=409, detail=f"Ingestion job {existing_running.id} is already running")

    job = IngestionJob(
        dataset_year=payload.dataset_year,
        source_url=str(payload.dataset_url),
        status="queued",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    async def worker() -> None:
        try:
            from app.db.session import AsyncSessionLocal

            async with AsyncSessionLocal() as worker_session:
                await worker_session.execute(
                    IngestionJob.__table__.update()
                    .where(IngestionJob.id == job.id)
                    .values(status="running")
                )
                await worker_session.commit()
                await _run_ingestion(payload.dataset_year, str(payload.dataset_url), worker_session)
        except Exception:  # noqa: BLE001
            logger.exception("Ingestion worker failed for job %s", job.id)

    background_tasks.add_task(worker)
    return IngestionTriggerResponse(job_id=job.id, status=job.status)


@router.get("/ingestion/jobs", dependencies=[Depends(get_admin_token)])
async def list_ingestion_jobs(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    jobs = (await session.execute(select(IngestionJob).order_by(desc(IngestionJob.started_at)).limit(50))).scalars().all()
    return [
        {
            "id": job.id,
            "dataset_year": job.dataset_year,
            "status": job.status,
            "records_processed": job.records_processed,
            "records_failed": job.records_failed,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }
        for job in jobs
    ]
