from elasticsearch import NotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query

from api.paginator import Paginator
from models.filmwork import BaseFilmwork, Filmwork
from services.filmwork import (
    FilmworksListService,
    FilmworksSearchService,
    RetrieveService,
    get_filmworks_list_service,
    get_filmworks_search_service,
    get_retrieve_filmwork_service,
)

router = APIRouter(tags=['filmworks'])


@router.get(
    '/filmworks',
    response_model=list[BaseFilmwork],
)
async def get_filmworks(
    service: FilmworksListService = Depends(get_filmworks_list_service),
    sort: str | None = Query(default=None, alias='sort_by'),
    genres: list[str] | None = Query(
        default=None,
        alias='filter[genres]',
        description='Filter by genres',
    ),
    paginator: Paginator = Depends(),
) -> list[BaseFilmwork]:
    filmworks = await service.get_objects(
        page_size=paginator.size,
        page_number=paginator.page,
        genres=genres,
        sort=sort,
    )
    return filmworks


@router.get(
    '/filmworks/search',
    response_model=list[BaseFilmwork],
    summary='Search filmworks',
    description='Full-text search by filmworks titles and descriptions',
)
async def search_filmworks(
    service: FilmworksSearchService = Depends(get_filmworks_search_service),
    query: str = Query(default=None, description='Search query'),
    paginator: Paginator = Depends(),
) -> list[BaseFilmwork]:
    filmworks = await service.get_objects(
        page_size=paginator.size,
        page_number=paginator.page,
        query=query,
    )
    return filmworks


@router.get(
    '/filmworks/{filmwork_pk}',
    response_model=Filmwork,
    summary='Filmwork page',
    description='Full information about the filmwork',
)
async def get_filmwork_by_pk(
    service: RetrieveService = Depends(get_retrieve_filmwork_service),
    filmwork_pk: str = None,
) -> Filmwork:
    try:
        filmwork = await service.get_by_pk(filmwork_pk)
        return filmwork
    except NotFoundError:
        raise HTTPException(status_code=404, detail='Filmwork not found')
