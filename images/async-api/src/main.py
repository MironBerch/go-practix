from contextlib import asynccontextmanager
from logging import DEBUG

import uvicorn
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.urls import api_router
from core.config import settings
from core.logger import LOGGING
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    elastic.elastic = AsyncElasticsearch(
        hosts=[
            f'http://{settings.elastic_host}:{settings.elastic_port}',
        ],
        http_auth=(settings.elastic_user, settings.elastic_password),
    )
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        db=settings.redis_db,
    )

    yield

    redis.redis.connection_pool.disconnect()
    await elastic.elastic.close()


app = FastAPI(
    title='Movies API v1',
    description='Read-only movies API',
    version='1.0',
    docs_url='/movies/api/docs',
    openapi_url='/movies/api/openapi.json',
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

app.include_router(api_router, prefix='/movies')

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        log_config=LOGGING,
        log_level=DEBUG,
        reload=True,
    )
