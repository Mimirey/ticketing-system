from pydantic import BaseModel, Field

class ApplicationCreate(BaseModel):
    company_ids: list[int] = Field(min_length=1)
    name: str
    description: str | None = None


class ApplicationUpdate(BaseModel):
    company_ids: list[int] = Field(min_length=1)
    name: str
    description: str | None = None


class CompanySummary(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class ApplicationResponse(BaseModel):
    id: int
    companies: list[CompanySummary]
    name: str
    description: str | None = None

    model_config = {
        "from_attributes": True
    }
