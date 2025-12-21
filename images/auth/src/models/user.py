import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email = Column(
        String(255),
        unique=True,
        index=True,
    )

    password_hash = Column(String(255))

    is_active = Column(Boolean())
    is_email_confirmed = Column(Boolean())

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    sessions = relationship(
        'Session',
        back_populates='user',
        lazy='selectin',
        order_by='Session.event_date.desc()',
        passive_deletes=True,
    )
