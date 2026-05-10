from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.security import AuthUser
from app.schemas.saved_company import SaveCompanyRequest, SavedCompanyResponse
from app.services.saved_company_service import list_saved_companies, remove_saved_company, save_company_for_user

router = APIRouter(prefix="/saved-companies", tags=["saved-companies"])


@router.get("", response_model=list[SavedCompanyResponse])
async def get_saved_companies(
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[SavedCompanyResponse]:
    return await list_saved_companies(session, user.user_id)


@router.post("", response_model=SavedCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_company(
    payload: SaveCompanyRequest,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> SavedCompanyResponse:
    saved = await save_company_for_user(session, user.user_id, user.email, payload.company_id)
    await session.commit()
    saved_companies = await list_saved_companies(session, user.user_id)
    for item in saved_companies:
        if item.id == saved.id:
            return item
    raise HTTPException(status_code=404, detail="Could not find saved company after creation")


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_company(
    company_id: int,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    deleted_count = await remove_saved_company(session, user.user_id, company_id)
    await session.commit()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved company not found")
