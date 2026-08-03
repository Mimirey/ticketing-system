from pydantic import BaseModel, field_validator

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v