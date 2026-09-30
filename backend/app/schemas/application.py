from pydantic import BaseModel

class ApplicationCreate(BaseModel):
    company_id: int
    name: str
    description: str | None = None
class ApplicationResponse(BaseModel):
    id:int
    company_id: int
    name: str
    description: str | None = None

    model_config ={
        "from_attributes": True
    }