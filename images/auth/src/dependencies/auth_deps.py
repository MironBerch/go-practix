from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db import redis
from src.utils.jwt_manager import jwt_manager

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cache_adapter: redis.RedisAdapter = Depends(redis.get_redis_adapter),
) -> str:
    """Зависимость для получения текущего пользователя из access токена"""
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)

    # Проверка типа токена
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token type',
        )

    # Проверка blacklist
    jti = payload.get('jti')
    if jti and await cache_adapter.get_object_from_cache(f'blacklist:{jti}'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has been revoked',
        )

    return payload.get('sub')


async def get_current_user_refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cache_adapter: redis.RedisAdapter = Depends(redis.get_redis_adapter),
) -> str:
    """Зависимость для получения пользователя из refresh токена"""
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)

    if payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token type',
        )

    # Проверка blacklist
    jti = payload.get('jti')
    if jti and await cache_adapter.get_object_from_cache(f'blacklist:{jti}'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has been revoked',
        )

    return payload.get('sub')
