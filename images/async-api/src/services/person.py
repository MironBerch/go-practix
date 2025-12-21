from uuid import UUID

from elasticsearch import AsyncElasticsearch

from fastapi import Depends

from db.elastic import get_elastic


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_person_filmworks(self, person_id: str) -> list[dict]:
        query = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'nested': {
                                'path': 'actors',
                                'query': {
                                    'match': {
                                        'actors.id': person_id,
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'directors',
                                'query': {
                                    'match': {
                                        'directors.id': person_id,
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'writers',
                                'query': {
                                    'match': {
                                        'writers.id': person_id,
                                    },
                                },
                            },
                        },
                    ],
                },
            },
            'sort': {
                'rating': {
                    'order': 'desc',
                },
            },
        }
        result = await self.elastic.search(index='movies', body=query)
        return result['hits']['hits']

    async def get_person_filmwork_ids_and_roles(
        self,
        person_id: str,
    ) -> dict[str, list[str | UUID]]:
        """Возвращает `id` фильмов в которых учавствовавала персона и его роли."""
        roles, filmwork_ids = set(), set()
        for hit in await self.get_person_filmworks(person_id):
            for actor in hit['_source']['actors']:
                if actor['id'] == person_id:
                    roles.add('actor')
                    filmwork_ids.add(hit['_source']['id'])
            for writer in hit['_source']['writers']:
                if writer['id'] == person_id:
                    roles.add('writer')
                    filmwork_ids.add(hit['_source']['id'])
            for director in hit['_source']['directors']:
                if director['id'] == person_id:
                    roles.add('director')
                    filmwork_ids.add(hit['_source']['id'])
        return {'roles': list(roles), 'filmwork_ids': list(filmwork_ids)}


def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic=elastic)
