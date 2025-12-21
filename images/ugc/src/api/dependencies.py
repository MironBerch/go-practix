from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException

from services.auth import AuthService
from services.filmworks import FilmworksService, get_filmworks_service
from services.reviews import ReviewsService, get_reviews_service


async def check_filmwork_exist(
    filmwork_id: UUID,
    filmworks_service: FilmworksService = Depends(get_filmworks_service),
):
    """Функция для проверки наличия фильма."""
    if not (await filmworks_service.get(filmwork_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


async def check_review_exists(
    filmwork_id: UUID,
    reviews_service: ReviewsService = Depends(get_reviews_service),
    auth: AuthService = Depends(),
):
    """Функция для проверки наличия обзора."""
    if not (await reviews_service.get(user_id=auth.user_id, filmwork_id=filmwork_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
