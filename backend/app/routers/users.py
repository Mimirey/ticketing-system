from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserResponse, UserCreate
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


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
    current_user: User = Depends(require_role("PM_IT"))
):
    if current_user.role.name != "PM_IT":
        raise HTTPException(
            status_code=403,
            detail="Hanya PM IT yang dapat membuat user"
        )
    existing_username = db.query(User).filter(
        User.username == data.username,
        User.is_deleted == False
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username sudah digunakan"
        )
    
    existing_email = db.query(User).filter(
        User.email == data.email,
        User.is_deleted == False
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email sudah digunakan"
        )
    user = User(
        username=data.username,
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=data.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PM_IT"))
):
    if current_user.role.name != "PM_IT":
        raise HTTPException(
            status_code=403,
            detail="Hanya PM IT yang dapat menghapus user"
        )
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan"
        )
    user.is_deleted = True
    db.commit()
    return {
        "message": "User berhasil dihapus"
    }