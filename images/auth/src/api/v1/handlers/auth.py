from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import mongo, redis
from src.core.config import settings
from src.db.postgres import get_async_session
from src.dependencies.auth_deps import get_current_user_refresh, security
from src.models.user import User
from src.schemas.schemas import SignInSchema, SignUpSchema
from src.utils import hash_password, mongo_users, sessions
from src.utils.jwt_manager import jwt_manager

router = APIRouter(tags=['auth'])


def create_full_tokens(user_id: str) -> tuple[str, str]:
    """Создание access и refresh токенов"""
    access_token = jwt_manager.create_access_token(user_id)
    refresh_token = jwt_manager.create_refresh_token(user_id)
    return access_token, refresh_token


@router.post('/signup', status_code=HTTPStatus.CREATED)
async def signup(
    data: SignUpSchema,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """User sign up"""
    try:
        result = await db.execute(select(User).where(User.email == data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='User with this email exists'
            )
        user = User(
            email=data.email,
            password_hash=hash_password.hash_password(data.password),
            is_active=True,
            is_email_confirmed=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        access_token, refresh_token = create_full_tokens(str(user.id))
        await sessions.create_session(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            db=db,
        )
        try:
            with mongo.get_mongo() as mongo_connection:
                mongo_users.create_user_by_id(mongo=mongo_connection, user_id=str(user.id))
        except Exception:
            ...
        return {
            'message': 'email confirmed',
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/signin', status_code=HTTPStatus.OK)
async def signin(
    data: SignInSchema,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """User sign in"""
    try:
        stmt = select(User).where(User.email == data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='user with this email does not exist'
            )
        if not hash_password.check_password(user.password_hash, data.password):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='password is not correct')
        access_token, refresh_token = create_full_tokens(str(user.id))
        await sessions.create_session(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            db=db,
        )
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/logout', status_code=HTTPStatus.OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cache_adapter: redis.RedisAdapter = Depends(redis.get_redis_adapter),
) -> dict[str, Any]:
    """User log out"""
    token = credentials.credentials
    try:
        # Получаем payload без проверки expiration (чтобы можно было logout с просроченным токеном)
        payload = jwt_manager.get_token_payload(token)
        jti = payload.get('jti')
        await cache_adapter.put_object_to_cache(
            f'blacklist:{jti}', 'revoked', ex=settings.security.jwt_refresh_token_expires
        )
        return {'message': 'logout completed'}
    except HTTPException:
        return {'message': 'logout completed'}


@router.post('/refresh', status_code=HTTPStatus.OK)
async def refresh(
    user_id: str = Depends(get_current_user_refresh),
    cache_adapter: redis.RedisAdapter = Depends(redis.get_redis_adapter),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Refresh token"""
    # Добавляем старый refresh токен в blacklist
    old_token = credentials.credentials
    old_payload = jwt_manager.get_token_payload(old_token)
    old_jti = old_payload.get('jti')
    await cache_adapter.put_object_to_cache(
        f'blacklist:{old_jti}', 'refreshed', ex=settings.security.jwt_refresh_token_expires
    )
    access_token = jwt_manager.create_access_token(user_id)
    return {'access_token': access_token}
