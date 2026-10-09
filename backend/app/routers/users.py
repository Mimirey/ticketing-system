import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.activity_log_utils import log_activity
from app.core.dependencies import get_current_user, require_role
from app.core.security import hash_password, verify_password
from app.db.database import get_db
from app.models.role import Role
from app.models.telegram_link_token import TelegramLinkToken
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    TelegramConnectRequest,
    UserCreate,
    UserResponse,
)
from app.services.telegram_link import link_telegram_account

router = APIRouter(prefix="/users", tags=["Users"])

DEFAULT_PASSWORD = "Admin123"


@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.name,
    }


@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = None,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.is_deleted == False)
    if role:
        query = query.join(User.role).filter(Role.name == role)
    return query.all()


@router.post("", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PM_IT")),
):
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        detail = "Username sudah digunakan"
        if existing_username.is_deleted:
            detail += " oleh akun yang sudah dihapus"
        raise HTTPException(status_code=400, detail=detail)

    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        detail = "Email sudah digunakan"
        if existing_email.is_deleted:
            detail += " oleh akun yang sudah dihapus"
        raise HTTPException(status_code=400, detail=detail)

    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role tidak valid")

    user = User(
        username=data.username,
        name=data.name,
        email=data.email,
        password_hash=hash_password(DEFAULT_PASSWORD),
        role_id=data.role_id,
        telegram_chat_id=data.telegram_chat_id,
    )
    db.add(user)

    try:
        log_activity(
            db,
            current_user.id,
            "CREATE_USER",
            f"{current_user.name} menambahkan user {user.name} dengan role {role.name}",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email atau username sudah digunakan",
        )

    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PM_IT")),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus akun sendiri")

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    user.is_deleted = True

    log_activity(
        db,
        current_user.id,
        "DELETE_USER",
        f"{current_user.name} menghapus user {user.name}",
    )

    db.commit()
    return {"message": "User berhasil dihapus"}


@router.post("/me/telegram/link")
def create_telegram_link(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(TelegramLinkToken).filter(
        TelegramLinkToken.user_id == current_user.id,
        TelegramLinkToken.used_at.is_(None),
    ).delete(synchronize_session=False)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    link_token = TelegramLinkToken(
        user_id=current_user.id,
        token=token,
        expires_at=expires_at,
    )
    db.add(link_token)
    db.commit()

    bot_username = "amazink_ticketing_bot"
    telegram_link = f"https://t.me/{bot_username}?start={token}"

    return {
        "message": "Link Telegram berhasil dibuat",
        "telegram_link": telegram_link,
        "expires_at": expires_at,
    }


@router.post("/me/telegram")
def connect_telegram(
    data: TelegramConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.telegram_chat_id = data.telegram_chat_id
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Telegram berhasil terhubung",
        "telegram_chat_id": current_user.telegram_chat_id,
    }


@router.patch("/me/password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password saat ini salah",
        )

    current_user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Password berhasil diubah"}


@router.post("/telegram/link/complete")
def complete_telegram_link(
    token: str,
    telegram_chat_id: str,
    db: Session = Depends(get_db),
):
    success, result = link_telegram_account(
        db=db,
        token=token,
        telegram_chat_id=telegram_chat_id,
    )
    if not success:
        raise HTTPException(status_code=400, detail=result)

    return {
        "message": "Telegram berhasil terhubung",
        "user_id": result.id,
    }


@router.patch("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PM_IT")),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_deleted == False,
        )
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan",
        )

    user.password_hash = hash_password(DEFAULT_PASSWORD)
    db.commit()

    return {"message": "Password berhasil di-reset menjadi password default"}