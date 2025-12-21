import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from core.config import settings


class JWTManager:
    def __init__(self):
        self.secret_key = settings.security.jwt_secret_key
        self.algorithm = settings.security.jwt_algorithm

    def create_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        token_type: str = 'access',
        **additional_claims,
    ) -> str:
        """Создание JWT токена"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.security.jwt_access_token_expires
            )

        to_encode = {
            'sub': subject,
            'exp': expire,
            'type': token_type,
            'jti': str(uuid.uuid4()),  # Unique token ID for blacklisting
            **additional_claims,
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_access_token(self, subject: str) -> str:
        """Создание access токена"""
        return self.create_token(
            subject=subject,
            expires_delta=timedelta(minutes=settings.security.jwt_access_token_expires),
            token_type='access',
        )

    def create_refresh_token(self, subject: str) -> str:
        """Создание refresh токена"""
        return self.create_token(
            subject=subject,
            expires_delta=timedelta(minutes=settings.security.jwt_refresh_token_expires),
            token_type='refresh',
        )

    def create_temp_token(self, subject: str) -> str:
        """Создание временного токена"""
        return self.create_token(
            subject=subject,
            expires_delta=timedelta(minutes=settings.security.jwt_temp_token_expires),
            token_type='temp',
        )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Верификация токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid token: {str(e)}',
            )

    def get_token_payload(self, token: str) -> Dict[str, Any]:
        """Получение payload из токена без верификации expiration"""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm], options={'verify_exp': False}
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid token: {str(e)}',
            )


# Создаем экземпляр менеджера
jwt_manager = JWTManager()
