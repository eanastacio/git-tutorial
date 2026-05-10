from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
