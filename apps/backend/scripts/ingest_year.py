import argparse
import asyncio
from pathlib import Path

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.scraper.dol_downloader import default_dataset_url, download_dataset
from app.services.ingestion_service import run_ingestion_job


async def ingest(dataset_year: int, dataset_url: str | None) -> None:
    settings = get_settings()
    source_url = dataset_url or default_dataset_url(dataset_year, settings.dol_dataset_base_url)
    dataset_path = await download_dataset(source_url, output_dir=Path("data"))

    async with AsyncSessionLocal() as session:
        job = await run_ingestion_job(
            session=session,
            dataset_year=dataset_year,
            source_url=source_url,
            dataset_path=dataset_path,
        )
        print(f"Job {job.id} completed with status={job.status} processed={job.records_processed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a yearly DOL LCA dataset")
    parser.add_argument("--year", type=int, required=True, help="Dataset fiscal year")
    parser.add_argument("--url", type=str, default=None, help="Optional explicit dataset URL")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(ingest(dataset_year=args.year, dataset_url=args.url))
