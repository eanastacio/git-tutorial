from __future__ import annotations

from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, SavedCompany, User
from app.schemas.company import CompanyListItem
from app.schemas.saved_company import SavedCompanyResponse


def _as_float(value: Decimal | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return value


async def ensure_user(session: AsyncSession, user_id: str, email: str | None = None) -> User:
    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user:
        return user
    user = User(id=user_id, email=email or f"{user_id}@unknown.local")
    session.add(user)
    await session.flush()
    return user


async def save_company_for_user(session: AsyncSession, user_id: str, email: str | None, company_id: int) -> SavedCompany:
    user = await ensure_user(session, user_id, email)
    existing = (
        await session.execute(
            select(SavedCompany).where(SavedCompany.user_id == user.id, SavedCompany.company_id == company_id)
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    saved = SavedCompany(user_id=user.id, company_id=company_id)
    session.add(saved)
    await session.flush()
    return saved


async def remove_saved_company(session: AsyncSession, user_id: str, company_id: int) -> int:
    result = await session.execute(
        delete(SavedCompany).where(SavedCompany.user_id == user_id, SavedCompany.company_id == company_id)
    )
    return result.rowcount or 0


async def list_saved_companies(session: AsyncSession, user_id: str) -> list[SavedCompanyResponse]:
    rows = (
        await session.execute(
            select(SavedCompany, Company)
            .join(Company, Company.id == SavedCompany.company_id)
            .where(SavedCompany.user_id == user_id)
            .order_by(SavedCompany.created_at.desc())
        )
    ).all()
    response: list[SavedCompanyResponse] = []
    for saved, company in rows:
        response.append(
            SavedCompanyResponse(
                id=saved.id,
                company=CompanyListItem(
                    id=company.id,
                    normalized_name=company.normalized_name,
                    display_name=company.display_name,
                    total_filings=company.total_filings,
                    total_certified=company.total_certified,
                    sponsorship_score=_as_float(company.sponsorship_score),
                    latest_filing_year=company.latest_filing_year,
                ),
            )
        )
    return response
