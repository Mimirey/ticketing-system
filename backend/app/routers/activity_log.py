from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse

router = APIRouter(prefix="/activity-logs", tags=["Activity Log"])
@router.get("", response_model=List[ActivityLogResponse])
def list_activity_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    return (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )