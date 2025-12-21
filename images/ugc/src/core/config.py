from os import environ

from pydantic import Field
from pydantic_settings import BaseSettings


class FastAPIConfig(BaseSettings):
    host: str = '0.0.0.0'
    port: int = int(environ.get('FASTAPI_PORT', 8000))
    debug: bool = environ.get('DEBUG') == 'True'


class MongoConfig(BaseSettings):
    host: str = environ.get('MONGO_HOST', 'mongo')
    port: int = int(environ.get('MONGO_PORT', 27017))
    username: str | None = environ.get('MONGO_USERNAME')
    password: str | None = environ.get('MONGO_PASSWORD')
    db: str = 'default'


class AuthConfig(BaseSettings):
    jwt_secret_key: str = environ.get('JWT_SECRET_KEY', 'jwt_secret_key')
    algorithm: str = 'HS256'


class Settings(BaseSettings):
    fastapi: FastAPIConfig = Field(default_factory=FastAPIConfig)
    mongo: MongoConfig = Field(default_factory=MongoConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)


settings = Settings()
