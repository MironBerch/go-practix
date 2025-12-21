from fastapi import Depends

from db.elastic import ElasticAdapter, get_elastic_adapter
from db.redis import RedisAdapter, get_redis_adapter
from models.filmwork import BaseFilmwork, Filmwork
from services.base import BaseListService, RetrieveService


class FilmworksListService(BaseListService):

    @staticmethod
    def get_elastic_query(genres: list[str] | None, sort: str | None) -> dict:
        query = {
            'query': {
                'bool': {},
            },
            'sort': {},
        }
        if sort:
            sort_field_mapping = {'title': 'title.raw', 'rating': 'rating'}
            field = sort.lstrip('-')
            elastic_field = sort_field_mapping.get(field, field)
            order = 'asc' if sort.startswith('-') else 'desc'
            query['sort'][elastic_field] = {'order': order}

        if genres:
            query['query']['bool']['must'] = [
                {
                    'terms': {
                        'genres': genres,
                    },
                },
            ]
        return query


class FilmworksSearchService(BaseListService):

    @staticmethod
    def get_elastic_query(query: str) -> dict:
        query = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['title', 'description'],
                },
            },
        }
        return query


def get_filmworks_list_service(
    redis: RedisAdapter = Depends(get_redis_adapter),
    elastic: ElasticAdapter = Depends(get_elastic_adapter),
) -> FilmworksListService:
    return FilmworksListService(
        cache_adapter=redis,
        db_adapter=elastic,
        index='movies',
        model=BaseFilmwork,
    )


def get_filmworks_search_service(
    redis: RedisAdapter = Depends(get_redis_adapter),
    elastic: ElasticAdapter = Depends(get_elastic_adapter),
) -> FilmworksSearchService:
    return FilmworksSearchService(
        cache_adapter=redis,
        db_adapter=elastic,
        index='movies',
        model=BaseFilmwork,
    )


def get_retrieve_filmwork_service(
    redis: RedisAdapter = Depends(get_redis_adapter),
    elastic: ElasticAdapter = Depends(get_elastic_adapter),
) -> RetrieveService:
    return RetrieveService(
        cache_adapter=redis,
        db_adapter=elastic,
        index='movies',
        model=Filmwork,
    )
