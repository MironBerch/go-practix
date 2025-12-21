from fastapi import APIRouter

from src.api.v1.handlers import filmwork, genre, health, person

api_v1_router = APIRouter(prefix='/v1')

# Healthcheck
api_v1_router.include_router(router=health.router)

# Filmworks
api_v1_router.include_router(router=filmwork.router)

# Genre
api_v1_router.include_router(router=genre.router)

# Person
api_v1_router.include_router(router=person.router)
