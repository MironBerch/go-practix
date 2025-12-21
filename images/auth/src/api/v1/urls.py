from fastapi import APIRouter

from src.api.v1.handlers import auth, health, user

api_v1_router = APIRouter(prefix='/v1')

# Healthcheck
api_v1_router.include_router(router=health.router)

# Auth
api_v1_router.include_router(router=auth.router)

# User
api_v1_router.include_router(router=user.router)
