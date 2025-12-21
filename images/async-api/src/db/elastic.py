import logging
from typing import Any

from elasticsearch import AsyncElasticsearch

logger = logging.getLogger()

elastic: AsyncElasticsearch


async def get_elastic() -> AsyncElasticsearch | None:
    return elastic


class ElasticAdapter:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_objects_from_db(
        self,
        index: str,
        model: Any,
        query: dict,
        page_size: int,
        page_number: int,
    ) -> list:
        data = await self.elastic.search(
            index=index,
            body={
                **query,
                'size': page_size,
                'from': (page_number - 1) * page_size,
            },
        )
        return [model(**document['_source']) for document in data['hits']['hits']]

    async def get_object_from_db(self, index: str, model: Any, object_pk: str):
        doc = await self.elastic.get(index=index, id=object_pk)
        return model(**doc['_source'])


def get_elastic_adapter() -> ElasticAdapter:
    return ElasticAdapter(elastic=elastic)
