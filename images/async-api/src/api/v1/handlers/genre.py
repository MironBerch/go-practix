from elasticsearch import NotFoundError

from fastapi import APIRouter, Depends, HTTPException

from models.genre import Genre
from services.genre import (
    GenresListService,
    RetrieveService,
    get_genres_list_service,
    get_retrieve_genre_service,
)

router = APIRouter(tags=['genres'])


@router.get(
    '/genres',
    response_model=list[Genre],
    summary='Genres',
    description='Genres list',
)
async def get_genres(
    service: GenresListService = Depends(get_genres_list_service),
) -> list[Genre]:
    genres = await service.get_objects()
    return genres


@router.get(
    '/genres/{genre_pk}',
    response_model=Genre,
    summary='Genre page',
    description='Genre information by pk',
)
async def get_genre_by_pk(
    service: RetrieveService = Depends(get_retrieve_genre_service),
    genre_pk: str = None,
) -> Genre:
    try:
        genre = await service.get_by_pk(genre_pk)
        return genre
    except NotFoundError:
        raise HTTPException(status_code=404, detail='Genre not found')
