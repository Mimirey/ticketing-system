from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.telegram_link_token import TelegramLinkToken

def link_telegram_account(
    db: Session,
    token: str,
    telegram_chat_id: str,
):
    link_token = db.query(TelegramLinkToken).filter(
        TelegramLinkToken.token == token,
        TelegramLinkToken.used_at.is_(None),
    ).first()
    if not link_token:
        return False, "Link Telegram tidak valid atau sudah digunakan"
    expires_at = link_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return False, "Link Telegram sudah kedaluwarsa"
    user = link_token.user
    user.telegram_chat_id = telegram_chat_id
    link_token.used_at = datetime.now(timezone.utc)
    db.commit()
    return True, user