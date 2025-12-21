from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent
from werkzeug.user_agent import UserAgent

from src.models.session import Session


def validate_user_device_type(user_agent_string: UserAgent) -> str:
    """
    Парсит данные `User-agent` и определяет с какого устройства вошёл пользователь.
    """
    device = None
    user_agent = parse_user_agent(user_agent_string)
    if user_agent.is_pc:
        device = 'pc'
    elif user_agent.is_tablet:
        device = 'tablet'
    elif user_agent.is_mobile:
        device = 'mobile'
    return device or 'other'


async def create_session(
    user_id: str | UUID,
    user_agent: str,
    db: AsyncSession,
) -> None:
    new_session = Session(
        user_id=user_id,
        user_agent=user_agent,
        user_device_type=validate_user_device_type(user_agent),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
