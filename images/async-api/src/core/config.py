from os import environ

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = environ.get('REDIS_HOST', 'redis')
    redis_port: int = int(environ.get('REDIS_PORT', 6379))
    redis_db: int = int(environ.get('REDIS_DB', 0))

    elastic_host: str = environ.get('ELASTIC_HOST', 'elastic')
    elastic_port: int = int(environ.get('ELASTIC_PORT', 9200))
    elastic_user: str = environ.get('ELASTIC_USER', 'elastic')
    elastic_password: str = environ.get('ELASTIC_PASSWORD', '')

    fastapi_host: str = '0.0.0.0'
    fastapi_port: int = int(environ.get('FASTAPI_PORT', 8000))


settings = Settings()
