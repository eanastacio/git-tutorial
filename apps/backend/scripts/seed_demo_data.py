import asyncio
from datetime import date
import hashlib

from sqlalchemy.dialects.postgresql import insert

from app.db.session import AsyncSessionLocal
from app.models.entities import Company, LCARecord
from app.services.ingestion_service import update_company_metrics

SEED_ROWS = [
    {
        "company": "Stripe",
        "job_title": "Software Engineer",
        "city": "San Francisco",
        "state": "CA",
        "wage": 185000,
        "wage_unit": "YEAR",
        "filing_year": 2025,
        "filing_date": date(2025, 1, 8),
        "case_status": "CERTIFIED",
        "visa_class": "H-1B",
    },
    {
        "company": "Google",
        "job_title": "Software Engineer Intern",
        "city": "Mountain View",
        "state": "CA",
        "wage": 9000,
        "wage_unit": "MONTH",
        "filing_year": 2025,
        "filing_date": date(2025, 2, 16),
        "case_status": "CERTIFIED",
        "visa_class": "H-1B",
    },
    {
        "company": "Deloitte",
        "job_title": "Business Analyst Program",
        "city": "New York",
        "state": "NY",
        "wage": 105000,
        "wage_unit": "YEAR",
        "filing_year": 2024,
        "filing_date": date(2024, 6, 4),
        "case_status": "CERTIFIED-WITHDRAWN",
        "visa_class": "H-1B",
    },
]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        company_stmt = insert(Company).values(
            [
                {"normalized_name": "stripe", "display_name": "Stripe"},
                {"normalized_name": "google", "display_name": "Google"},
                {"normalized_name": "deloitte", "display_name": "Deloitte"},
            ]
        )
        company_stmt = company_stmt.on_conflict_do_nothing(index_elements=[Company.normalized_name])
        await session.execute(company_stmt)
        await session.commit()

        companies = (
            await session.execute(
                Company.__table__.select().where(Company.normalized_name.in_(["stripe", "google", "deloitte"]))
            )
        ).all()
        company_map = {row.normalized_name: row.id for row in companies}

        payload = []
        for row in SEED_ROWS:
            normalized = row["company"].lower()
            record_hash = hashlib.sha256(
                f"{row['company']}|{row['job_title']}|{row['city']}|{row['state']}|{row['filing_year']}".encode("utf-8")
            ).hexdigest()
            payload.append(
                {
                    "company_id": company_map[normalized],
                    "case_number": f"CASE-{record_hash[:10]}",
                    "job_title": row["job_title"],
                    "soc_code": "15-1252",
                    "city": row["city"],
                    "state": row["state"],
                    "wage": row["wage"],
                    "wage_unit": row["wage_unit"],
                    "filing_year": row["filing_year"],
                    "filing_date": row["filing_date"],
                    "case_status": row["case_status"],
                    "visa_class": row["visa_class"],
                    "worksite_location": f"{row['city']}, {row['state']}",
                    "is_internship_role": "intern" in row["job_title"].lower(),
                    "is_new_grad_role": "program" in row["job_title"].lower(),
                    "remote_type": "on-site",
                    "record_hash": record_hash,
                }
            )
        lca_stmt = insert(LCARecord).values(payload).on_conflict_do_nothing(index_elements=[LCARecord.record_hash])
        await session.execute(lca_stmt)
        await session.commit()
        await update_company_metrics(session, set(company_map.values()))
        await session.commit()

    print("Seed data inserted.")


if __name__ == "__main__":
    asyncio.run(main())
