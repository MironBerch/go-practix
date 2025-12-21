import logging
from http import HTTPStatus
from uuid import UUID

import jwt
from jwt.exceptions import ExpiredSignatureError

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

security = HTTPBearer(auto_error=not settings.fastapi.debug)


class AuthService:
    def __init__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Принимает в HTTP-запросе заголовок с JWT-токеном."""
        if credentials:
            self.token = credentials.credentials
        else:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    def decode_token(self) -> dict:
        """Декодирование JWT-токена."""
        try:
            payload = jwt.decode(
                self.token,
                key=settings.auth.jwt_secret_key,
                algorithms=[settings.auth.algorithm],
            )
        except ExpiredSignatureError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
        except Exception as exc:
            logging.error(f'Проблема с авторизацией пользователей: {exc}!')
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)
        return payload

    @property
    def user_id(self) -> UUID:
        """Получение с user ID пользователя из claims токена."""
        claims = self.decode_token()
        if not (user_id := claims.get('sub')):
            logging.error('Проблема с получением user_id: В токене нет ID пользователя!')
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)
        return UUID(user_id)
