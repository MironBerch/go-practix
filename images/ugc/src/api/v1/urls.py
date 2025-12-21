from fastapi import APIRouter

from src.api.v1.handlers import bookmarks, fimworks, reviews

api_v1_router = APIRouter(prefix='/v1')

api_v1_router.include_router(router=bookmarks.router)
api_v1_router.include_router(router=reviews.router)
api_v1_router.include_router(router=fimworks.router)
