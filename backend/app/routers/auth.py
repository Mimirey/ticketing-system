# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.activity_log_utils import log_activity
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == data.email, User.is_deleted == False)
        .first()
    )

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
        )

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    log_activity(db, user.id, "LOGIN", f"{user.name} melakukan login")
    db.commit()
    return LoginResponse(
        access_token=token,
        role=user.role.name,
        name=user.name,
    )