from os import environ

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    host: str = environ.get('DB_HOST', 'db')
    port: int = int(environ.get('DB_PORT', 5432))
    db: str = environ.get('DB_NAME', 'auth')
    user: str = environ.get('DB_USER', 'postgres')
    password: SecretStr = SecretStr(environ.get('DB_PASSWORD', 'postgres'))


class RedisConfig(BaseSettings):
    host: str = environ.get('REDIS_HOST', 'redis')
    port: int = int(environ.get('REDIS_PORT', 6379))
    db: int = int(environ.get('REDIS_DB', 1))


class FastAPIConfig(BaseSettings):
    host: str = '0.0.0.0'
    port: int = int(environ.get('FASTAPI_PORT', 8000))
    secret_key: SecretStr = SecretStr(environ.get('SECRET_KEY', 'secret_key'))
    debug: bool = environ.get('DEBUG') == 'True'


class SecurityConfig(BaseSettings):
    jwt_secret_key: str = environ.get('JWT_SECRET_KEY', 'jwt_secret_key')
    jwt_temp_token_expires: int = 60 * 60
    jwt_access_token_expires: int = 24 * 60 * 60
    jwt_refresh_token_expires: int = 30 * 24 * 60 * 60
    jwt_algorithm: str = 'HS256'


class Settings(BaseSettings):
    fastapi: FastAPIConfig = Field(default_factory=FastAPIConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)


settings = Settings()
