from pydantic import BaseModel, field_validator, EmailStr
from app.core.validators import validate_password


class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    role_id: int
    telegram_chat_id: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    username: str | None = None
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


class TelegramConnectRequest(BaseModel):
    telegram_chat_id: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        validate_password(value)
        return value