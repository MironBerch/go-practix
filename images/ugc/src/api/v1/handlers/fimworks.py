from uuid import UUID

from fastapi import APIRouter, Depends, Path

from api.dependencies import check_filmwork_exist
from models.models import Rating, Score
from services.auth import AuthService
from services.filmworks import FilmworksService, get_filmworks_service

router = APIRouter(tags=['filmworks'])


@router.get(
    path='/filmworks/{filmwork_id}/ratings',
    summary='Просмотр рейтинга фильма',
    response_description='Рейтинг фильма',
    response_model=Rating,
    dependencies=[Depends(check_filmwork_exist)],
)
async def get_filmwork_rating(
    service: FilmworksService = Depends(get_filmworks_service),
    filmwork_id: UUID = Path(title='UUID фильма'),
) -> Rating:
    result = await service.get_rating(filmwork_id=filmwork_id)
    return result


@router.post(
    path='/filmworks/{filmwork_id}/ratings',
    summary='Добавление оценки фильму',
    response_description='Рейтинг фильма',
    response_model=Rating,
    dependencies=[Depends(check_filmwork_exist)],
)
async def rate_filmwork(
    score: Score,
    auth: AuthService = Depends(),
    service: FilmworksService = Depends(get_filmworks_service),
    filmwork_id: UUID = Path(title='UUID фильма'),
) -> Rating:
    result = await service.rate(filmwork_id=filmwork_id, user_id=auth.user_id, score=score.score)
    return result


@router.delete(
    path='/filmworks/{filmwork_id}/ratings',
    summary='Удаление оценки у фильма',
    response_description='Результат удаление оценки у фильма',
    response_model=Rating,
    dependencies=[Depends(check_filmwork_exist)],
)
async def unrate_filmwork(
    auth: AuthService = Depends(),
    service: FilmworksService = Depends(get_filmworks_service),
    filmwork_id: UUID = Path(title='UUID фильма'),
) -> Rating:
    result = await service.unrate(filmwork_id=filmwork_id, user_id=auth.user_id)
    return result
