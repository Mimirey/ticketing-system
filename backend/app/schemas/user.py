from pydantic import BaseModel, field_validator, EmailStr
from app.core.validators import validate_password

class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    role_id: int
    @field_validator("password")
    @classmethod
    def validate_password_field(cls, value:str)-> str:
        validate_password(value)
        return value

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    username: str | None=None
    is_active: bool
    is_deleted: bool

    class Config:
        from_attributes = True
    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v