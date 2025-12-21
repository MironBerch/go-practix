from contextlib import asynccontextmanager
from logging import DEBUG
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.urls import api_router
from core.config import settings
from core.logger import LOGGING
from db import mongo, redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    redis.redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=True,
    )
    mongo.start()

    yield

    await redis.redis.connection_pool.disconnect()
    mongo.stop()


app = FastAPI(
    title='Auth API v1',
    description='Auth API',
    version='1.0',
    docs_url='/auth/api/docs',
    openapi_url='/auth/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix='/auth')

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.fastapi.host,
        port=settings.fastapi.port,
        log_config=LOGGING,
        log_level=DEBUG,
        reload=True,
    )
