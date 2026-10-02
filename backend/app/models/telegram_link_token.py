from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class TelegramLinkToken(Base):
    __tablename__ = "telegram_link_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    token = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )
    used_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    user = relationship(
        "User",
        backref="telegram_link_tokens"
    )