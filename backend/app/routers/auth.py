# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.limiter import limiter
from app.db.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token
from app.core.activity_log_utils import log_activity
from app.models.user import User
from app.core.captcha import generate_captcha, verify_captcha
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, RefreshTokenRequest, CaptchaResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse) 
@limiter.limit("5/minute") 
def login( 
    data: LoginRequest, 
    request: Request, 
    db: Session = Depends(get_db) ): 
    if not verify_captcha( 
        data.captcha_id, 
        data.captcha_answer 
    ): 
        raise HTTPException( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="CAPTCHA tidak valid atau sudah kedaluwarsa" 
            ) 
    user = ( 
        db.query(User)
          .filter( or_( 
              User.email == data.identifier, 
              User.username == data.identifier 
              )
         ) 
         .first() 
    ) 
    if not user: 
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Username/email atau password salah", 
        )  
    if user.is_deleted: 
        raise HTTPException( 
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Akun sudah dinonaktifkan. Silakan hubungi administrator.", 
        )
    if not user.is_active: 
        raise HTTPException( 
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Akun sedang dinonaktifkan. Silakan hubungi administrator.", 
        )
    if not verify_password(data.password, user.password_hash): 
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Username/email atau password salah", 
            ) 
    token = create_access_token( 
        data={"sub": str(user.id), "role": user.role.name} 
    ) 
    refresh_token = create_refresh_token( 
        data={"sub": str(user.id), "role": user.role.name} 
    ) 
    log_activity( db, user.id, "LOGIN", f"{user.name} melakukan login" ) 
    db.commit() 
    return LoginResponse( 
        access_token=token, 
        refresh_token=refresh_token, 
        id=user.id, 
        role=user.role.name, 
        name=user.name, 
    )

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
def refresh_access_token(data: RefreshTokenRequest, request: Request):
    payload = decode_refresh_token(data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token tidak valid",
        )

    new_access_token = create_access_token(
        data={
            "sub": payload["sub"],
            "role": payload["role"]
        }
    )
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=data.refresh_token
    )
@router.get("/captcha", response_model=CaptchaResponse)
def get_captcha():
    captcha_id, question = generate_captcha()

    return CaptchaResponse(
        captcha_id=captcha_id,
        question=question
    )