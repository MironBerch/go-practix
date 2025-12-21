from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query

from api.paginator import Paginator
from db.elastic import get_elastic
from models.filmwork import BaseFilmwork
from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter(tags=['persons'])


@router.get(
    '/persons',
    response_model=list[Person],
    summary='Persons',
    description='Persons list',
)
async def get_persons(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    paginator: Paginator = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    query = {
        'query': {
            'match_all': {},
        },
        'from': (paginator.page - 1) * paginator.size,
        'size': paginator.size,
    }
    result = await elastic.search(
        index='persons',
        body=query,
    )
    persons: list[dict[str, Any]] = []
    for person in result['hits']['hits']:
        filmwork_ids_and_roles = await person_service.get_person_filmwork_ids_and_roles(
            person_id=person['_source']['id'],
        )
        person['_source']['filmwork_ids'] = filmwork_ids_and_roles['filmwork_ids']
        person['_source']['roles'] = filmwork_ids_and_roles['roles']
        persons.append(person['_source'])
    return [Person(**person) for person in persons]


@router.get(
    '/persons/search',
    response_model=list[Person],
    summary='Search persons',
    description='Full-text search by persons names',
)
async def search_persons(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    query: str = Query(default=None, description='Search query'),
    paginator: Paginator = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    query = {
        'query': {
            'match': {
                'full_name': query,
            },
        },
        'from': (paginator.page - 1) * paginator.size,
        'size': paginator.size,
    }
    result = await elastic.search(
        index='persons',
        body=query,
    )
    persons: list[dict[str, Any]] = []
    for person in result['hits']['hits']:
        filmwork_ids_and_roles = await person_service.get_person_filmwork_ids_and_roles(
            person_id=person['_source']['id'],
        )
        person['_source']['filmwork_ids'] = filmwork_ids_and_roles['filmwork_ids']
        person['_source']['roles'] = filmwork_ids_and_roles['roles']
        persons.append(person['_source'])
    return [Person(**person) for person in persons]


@router.get(
    '/persons/{person_pk}',
    response_model=Person,
    summary='Person page',
    description='Full information about the person',
)
async def get_person_by_pk(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    person_pk: str = None,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    try:
        result = await elastic.get(index='persons', id=person_pk)
        filmwork_ids_and_roles = await person_service.get_person_filmwork_ids_and_roles(
            person_id=result['_source']['id'],
        )
        result['_source']['filmwork_ids'] = filmwork_ids_and_roles['filmwork_ids']
        result['_source']['roles'] = filmwork_ids_and_roles['roles']
        return Person(**result['_source'])
    except NotFoundError:
        raise HTTPException(status_code=404, detail='Person not found')


@router.get(
    '/persons/{person_pk}/filmworks',
    response_model=list[BaseFilmwork],
    summary='Filmworks by person',
    description='Filmworks of the person',
)
async def get_person_filmworks_by_pk(
    person_pk: str = None,
    person_service: PersonService = Depends(get_person_service),
) -> list[BaseFilmwork]:
    return [
        BaseFilmwork(
            **filmwork['_source'],
        )
        for filmwork in await person_service.get_person_filmworks(
            person_id=person_pk,
        )
    ]
