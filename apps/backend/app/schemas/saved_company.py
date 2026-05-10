from pydantic import BaseModel

from app.schemas.company import CompanyListItem


class SaveCompanyRequest(BaseModel):
    company_id: int


class SavedCompanyResponse(BaseModel):
    id: int
    company: CompanyListItem
