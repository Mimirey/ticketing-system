# app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    id: int
    role: str
    name: str
class RefreshTokenRequest(BaseModel):
    refresh_token: str
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"