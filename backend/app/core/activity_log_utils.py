from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog

def log_activity(db: Session, user_id: int | None, action: str, description: str):
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
    )
    db.add(entry)