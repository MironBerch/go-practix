from fastapi import Depends

from db.elastic import ElasticAdapter, get_elastic_adapter
from db.redis import RedisAdapter, get_redis_adapter
from models.genre import Genre
from services.base import BaseListService, RetrieveService


class GenresListService(BaseListService):

    @staticmethod
    def get_elastic_query():
        query = {
            'query': {
                'match_all': {},
            },
            'size': 1000,
        }
        return query


def get_genres_list_service(
    redis: RedisAdapter = Depends(get_redis_adapter),
    elastic: ElasticAdapter = Depends(get_elastic_adapter),
) -> GenresListService:
    return GenresListService(
        cache_adapter=redis,
        db_adapter=elastic,
        index='genres',
        model=Genre,
    )


def get_retrieve_genre_service(
    redis: RedisAdapter = Depends(get_redis_adapter),
    elastic: ElasticAdapter = Depends(get_elastic_adapter),
) -> RetrieveService:
    return RetrieveService(
        cache_adapter=redis,
        db_adapter=elastic,
        index='genres',
        model=Genre,
    )
