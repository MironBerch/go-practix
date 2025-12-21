import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


class Session(Base):
    """Модель сессии пользователя."""

    __tablename__ = 'sessions'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_date = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    user_agent = Column(String)
    user_device_type = Column(String)

    user = relationship('User', back_populates='sessions')
