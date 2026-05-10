from pydantic import BaseModel, HttpUrl


class IngestionTriggerRequest(BaseModel):
    dataset_year: int
    dataset_url: HttpUrl


class IngestionTriggerResponse(BaseModel):
    job_id: int
    status: str
