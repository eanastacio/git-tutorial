from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from typing import Any

from app.normalization.company_normalizer import display_company_name, normalize_company_name
from app.normalization.location_normalizer import normalize_city, normalize_state

INTERN_KEYWORDS = ("intern", "internship", "co-op", "coop")
NEW_GRAD_KEYWORDS = (
    "new grad",
    "campus",
    "university",
    "analyst program",
    "associate program",
    "entry level",
)


@dataclass
class ProcessedLCARecord:
    case_number: str
    normalized_company_name: str
    display_company_name: str
    job_title: str
    soc_code: str | None
    city: str
    state: str
    wage: float | None
    wage_unit: str | None
    filing_year: int
    filing_date: datetime | None
    case_status: str
    visa_class: str
    worksite_location: str
    is_internship_role: bool
    is_new_grad_role: bool
    remote_type: str
    record_hash: str


def _parse_wage(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).replace("$", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return round(float(text), 2)
    except ValueError:
        return None


def _parse_date(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _infer_remote_type(job_title: str, worksite: str) -> str:
    haystack = f"{job_title} {worksite}".lower()
    if "hybrid" in haystack:
        return "hybrid"
    if "remote" in haystack or "telecommute" in haystack:
        return "remote"
    return "on-site"


def _contains_keywords(value: str, keywords: tuple[str, ...]) -> bool:
    content = value.lower()
    return any(keyword in content for keyword in keywords)


def _build_hash(parts: list[str]) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def process_raw_row(raw: dict[str, Any]) -> ProcessedLCARecord:
    company_raw = str(raw.get("EMPLOYER_NAME") or raw.get("employer_name") or "").strip()
    job_title = str(raw.get("JOB_TITLE") or raw.get("job_title") or "").strip().title()
    city = normalize_city(str(raw.get("WORKSITE_CITY") or raw.get("city") or "Unknown"))
    state = normalize_state(str(raw.get("WORKSITE_STATE") or raw.get("state") or "NA"))
    filing_date = _parse_date(raw.get("CASE_SUBMITTED") or raw.get("filing_date"))
    filing_year = int(raw.get("YEAR") or raw.get("filing_year") or (filing_date.year if filing_date else datetime.utcnow().year))
    case_status = str(raw.get("CASE_STATUS") or raw.get("case_status") or "UNKNOWN").upper().strip()
    visa_class = str(raw.get("VISA_CLASS") or raw.get("visa_class") or "H-1B").upper().strip()
    case_number = str(raw.get("CASE_NUMBER") or raw.get("case_number") or "")
    wage = _parse_wage(raw.get("WAGE_RATE_OF_PAY_FROM") or raw.get("wage"))
    wage_unit = str(raw.get("WAGE_UNIT_OF_PAY") or raw.get("wage_unit") or "").upper().strip() or None
    worksite_location = re.sub(r"\s+", " ", str(raw.get("WORKSITE") or f"{city}, {state}")).strip()
    remote_type = _infer_remote_type(job_title, worksite_location)
    is_internship = _contains_keywords(job_title, INTERN_KEYWORDS)
    is_new_grad = _contains_keywords(job_title, NEW_GRAD_KEYWORDS)
    normalized_company = normalize_company_name(company_raw)
    display_name = display_company_name(company_raw)
    record_hash = _build_hash(
        [
            case_number,
            normalized_company,
            job_title,
            city,
            state,
            str(filing_year),
            visa_class,
        ]
    )

    return ProcessedLCARecord(
        case_number=case_number,
        normalized_company_name=normalized_company,
        display_company_name=display_name,
        job_title=job_title,
        soc_code=(raw.get("SOC_CODE") or raw.get("soc_code") or None),
        city=city,
        state=state,
        wage=wage,
        wage_unit=wage_unit,
        filing_year=filing_year,
        filing_date=filing_date,
        case_status=case_status,
        visa_class=visa_class,
        worksite_location=worksite_location,
        is_internship_role=is_internship,
        is_new_grad_role=is_new_grad,
        remote_type=remote_type,
        record_hash=record_hash,
    )
