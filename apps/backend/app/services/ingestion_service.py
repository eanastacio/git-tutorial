from __future__ import annotations

from datetime import datetime
from pathlib import Path
import zipfile
import logging

import pandas as pd
from sqlalchemy import case, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, IngestionFailure, IngestionJob, LCARecord
from app.processors.lca_processor import process_raw_row
from app.services.sponsorship_score import compute_sponsorship_score

logger = logging.getLogger(__name__)

CHUNK_SIZE = 15_000


def _extract_csv_file(dataset_path: Path) -> Path:
    if dataset_path.suffix.lower() == ".csv":
        return dataset_path
    if dataset_path.suffix.lower() != ".zip":
        raise ValueError(f"Unsupported dataset format: {dataset_path}")

    extracted_dir = dataset_path.parent / dataset_path.stem
    extracted_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dataset_path, "r") as zip_ref:
        zip_ref.extractall(extracted_dir)
    csv_files = list(extracted_dir.glob("*.csv"))
    if not csv_files:
        raise ValueError("No CSV file found in dataset archive")
    return csv_files[0]


async def _upsert_companies(session: AsyncSession, names: dict[str, str]) -> None:
    if not names:
        return
    payload = [{"normalized_name": normalized, "display_name": display} for normalized, display in names.items()]
    stmt = insert(Company).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Company.normalized_name],
        set_={"display_name": stmt.excluded.display_name},
    )
    await session.execute(stmt)


async def _company_id_map(session: AsyncSession, normalized_names: set[str]) -> dict[str, int]:
    rows = (
        await session.execute(
            select(Company.id, Company.normalized_name).where(Company.normalized_name.in_(normalized_names))
        )
    ).all()
    return {normalized_name: company_id for company_id, normalized_name in rows}


async def _insert_lca_records(session: AsyncSession, payload: list[dict]) -> int:
    if not payload:
        return 0
    stmt = insert(LCARecord).values(payload)
    stmt = stmt.on_conflict_do_nothing(index_elements=[LCARecord.record_hash])
    result = await session.execute(stmt)
    return result.rowcount or 0


async def update_company_metrics(session: AsyncSession, company_ids: set[int]) -> None:
    if not company_ids:
        return
    rows = (
        await session.execute(
            select(
                LCARecord.company_id,
                func.count(LCARecord.id),
                func.sum(case((LCARecord.case_status.like("CERTIFIED%"), 1), else_=0)),
                func.sum(case((LCARecord.filing_year >= datetime.utcnow().year - 2, 1), else_=0)),
                func.sum(case((LCARecord.is_internship_role.is_(True), 1), else_=0)),
                func.count(func.distinct(LCARecord.filing_year)),
                func.min(LCARecord.filing_year),
                func.max(LCARecord.filing_year),
            )
            .where(LCARecord.company_id.in_(company_ids))
            .group_by(LCARecord.company_id)
        )
    ).all()

    for (
        company_id,
        total_filings,
        total_certified,
        recent_filings,
        internship_filings,
        unique_years,
        min_year,
        max_year,
    ) in rows:
        total_filings = total_filings or 0
        total_certified = total_certified or 0
        recent_filings = recent_filings or 0
        internship_filings = internship_filings or 0
        year_span = ((max_year - min_year + 1) if min_year and max_year else 1) or 1
        consistency_ratio = min(unique_years / year_span, 1.0) if unique_years else 0
        certification_rate = total_certified / total_filings if total_filings else 0
        internship_ratio = internship_filings / total_filings if total_filings else 0
        score = compute_sponsorship_score(
            total_filings=total_filings,
            recent_filings=recent_filings,
            certification_rate=certification_rate,
            internship_ratio=internship_ratio,
            consistency_ratio=consistency_ratio,
        )
        await session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(
                total_filings=total_filings,
                total_certified=total_certified,
                latest_filing_year=max_year,
                sponsorship_score=score,
            )
        )


async def run_ingestion_job(session: AsyncSession, dataset_year: int, source_url: str, dataset_path: Path) -> IngestionJob:
    job = IngestionJob(dataset_year=dataset_year, source_url=source_url, status="running")
    session.add(job)
    await session.flush()
    await session.commit()

    logger.info("Started ingestion job id=%s year=%s", job.id, dataset_year)
    csv_path = _extract_csv_file(dataset_path)
    company_ids_touched: set[int] = set()
    total_processed = 0
    total_failed = 0

    try:
        for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE, dtype=str, low_memory=False):
            processed_payload: list[dict] = []
            failures: list[IngestionFailure] = []
            company_names: dict[str, str] = {}

            for row in chunk.fillna("").to_dict("records"):
                try:
                    processed = process_raw_row(row)
                    company_names[processed.normalized_company_name] = processed.display_company_name
                    processed_payload.append(
                        {
                            "case_number": processed.case_number,
                            "job_title": processed.job_title,
                            "soc_code": processed.soc_code,
                            "city": processed.city,
                            "state": processed.state,
                            "wage": processed.wage,
                            "wage_unit": processed.wage_unit,
                            "filing_year": processed.filing_year,
                            "filing_date": processed.filing_date.date() if processed.filing_date else None,
                            "case_status": processed.case_status,
                            "visa_class": processed.visa_class,
                            "worksite_location": processed.worksite_location,
                            "is_internship_role": processed.is_internship_role,
                            "is_new_grad_role": processed.is_new_grad_role,
                            "remote_type": processed.remote_type,
                            "record_hash": processed.record_hash,
                            "_normalized_name": processed.normalized_company_name,
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    failures.append(IngestionFailure(job_id=job.id, reason=str(exc), raw_payload=row))

            await _upsert_companies(session, company_names)
            mapping = await _company_id_map(session, set(company_names.keys()))
            for item in processed_payload:
                normalized_name = item.pop("_normalized_name")
                company_id = mapping.get(normalized_name)
                if not company_id:
                    failures.append(
                        IngestionFailure(
                            job_id=job.id,
                            reason=f"Could not map company '{normalized_name}'",
                            raw_payload=item,
                        )
                    )
                    continue
                item["company_id"] = company_id
                company_ids_touched.add(company_id)

            inserted_count = await _insert_lca_records(
                session,
                [item for item in processed_payload if "company_id" in item],
            )
            if failures:
                session.add_all(failures)

            total_processed += inserted_count
            total_failed += len(failures)
            await session.commit()

        await update_company_metrics(session, company_ids_touched)
        await session.execute(
            update(IngestionJob)
            .where(IngestionJob.id == job.id)
            .values(
                status="completed",
                records_processed=total_processed,
                records_failed=total_failed,
                completed_at=datetime.utcnow(),
            )
        )
        await session.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ingestion failed for job %s", job.id)
        await session.execute(
            update(IngestionJob)
            .where(IngestionJob.id == job.id)
            .values(
                status="failed",
                records_processed=total_processed,
                records_failed=total_failed,
                completed_at=datetime.utcnow(),
                error_message=str(exc),
            )
        )
        await session.commit()
        raise

    refreshed = (await session.execute(select(IngestionJob).where(IngestionJob.id == job.id))).scalar_one()
    return refreshed
