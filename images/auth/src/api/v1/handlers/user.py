from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_async_session
from src.dependencies.auth_deps import get_current_user
from src.models.session import Session
from src.models.user import User
from src.schemas.schemas import EmailSchema, PasswordChangeSchema, UserSessionSchema
from src.utils import hash_password

router = APIRouter(tags=['user'])


@router.get('/user_info', status_code=HTTPStatus.OK)
async def get_user_info(
    user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)
) -> dict[str, Any]:
    """Get user info"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    return {
        'user_id': user.id,
        'user_created_at': user.created_at,
        'user_email': user.email,
        'is_email_confirmed': user.is_email_confirmed,
    }


@router.post('/password_change', status_code=HTTPStatus.OK)
async def password_change(
    data: PasswordChangeSchema,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Change user password"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

        user.password_hash = hash_password.hash_password(data.new_password)
        await db.commit()
        return {'message': 'password changed'}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/change_email', status_code=HTTPStatus.OK)
async def change_email(
    data: EmailSchema,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Change user email"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
        stmt = select(User).where(User.email == data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail='user with this email exist'
            )
        user.email = data.email
        await db.commit()
        return {'message': 'email changed'}
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/user_sessions', status_code=HTTPStatus.OK)
async def get_user_sessions(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> List[UserSessionSchema]:
    """Get user sessions"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    stmt = select(Session).where(Session.user_id == user.id)
    result = await db.execute(stmt)
    user_sessions = result.scalars().all()
    return [
        UserSessionSchema(
            user_id=str(session.user_id),
            user_agent=session.user_agent,
            event_date=session.event_date,
            user_device_type=session.user_device_type,
        )
        for session in user_sessions
    ]
