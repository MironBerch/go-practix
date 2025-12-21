from contextlib import asynccontextmanager
from logging import DEBUG

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.urls import api_router
from core.config import settings
from db import mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.start()

    yield

    await mongo.stop()


app = FastAPI(
    title='Movies UGC v1',
    description='Movies UGC',
    version='1.0',
    docs_url='/ugc/api/docs',
    openapi_url='/ugc/api/openapi.json',
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

app.include_router(api_router)


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.fastapi.host,
        port=settings.fastapi.port,
        log_level=DEBUG,
        reload=True,
    )
