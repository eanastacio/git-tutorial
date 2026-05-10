from __future__ import annotations

from pathlib import Path
import logging

import httpx

logger = logging.getLogger(__name__)


def default_dataset_url(dataset_year: int, base_url: str) -> str:
    return f"{base_url}/LCA_Disclosure_Data_FY{dataset_year}.zip"


async def download_dataset(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = url.split("/")[-1]
    output_path = output_dir / filename
    logger.info("Downloading dataset from %s", url)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        output_path.write_bytes(response.content)

    logger.info("Saved dataset to %s", output_path)
    return output_path
