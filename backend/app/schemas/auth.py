# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
class CaptchaResponse(BaseModel):
    captcha_id:str
    question: str

class LoginRequest(BaseModel):
    identifier: str
    password: str
    captcha_id: str
    captcha_answer:int

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