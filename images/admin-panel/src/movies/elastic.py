import logging
from typing import Any
from uuid import UUID

from elasticsearch import Elasticsearch

from config import settings
from movies.models import Filmwork, Genre, Person

logger = logging.getLogger(__name__)


class ElasticsearchStartUpService:
    def __init__(self) -> None:
        self.client = Elasticsearch(
            f'http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}',
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        )

    def create_indices(self) -> None:
        """Создаёт индексы если они не существуют"""

        for index_name, mapping in settings.ELASTICSEARCH_INDICES.items():
            if not self.client.indices.exists(index=index_name):
                try:
                    body = {
                        "settings": settings.ELASTICSEARCH_SETTINGS,
                        "mappings": {"dynamic": "strict", "properties": mapping},
                    }
                    self.client.indices.create(index=index_name, body=body)
                    logger.info(f"Создан индекс: {index_name}")
                except Exception as e:
                    logger.info(f"Индекс не создан: {index_name}")
                    logger.error(f"Индекс не создан: {e}")


class ElasticsearchService:
    """Сервис для работы с Elasticsearch из админ-панели"""

    def __init__(self) -> None:
        self.client = Elasticsearch(
            f'http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}',
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        )

    def index_filmwork(self, filmwork: Filmwork) -> bool:
        """Индексирует фильм в Elasticsearch"""
        try:
            # Преобразуем Django модель в формат для Elasticsearch
            doc = self._filmwork_to_document(filmwork)
            print(doc)
            self.client.index(
                index="movies", id=str(filmwork.id), body=doc, refresh=True  # Синхронное обновление
            )
            logger.info(f"Фильм индексирован: {filmwork.title}")
            return True
        except Exception as e:
            logger.error(f"Ошибка индексации фильма {filmwork.id}: {e}")
            return False

    def index_person(self, person: Person) -> bool:
        """Индексирует персону в Elasticsearch"""
        try:
            doc = {"id": str(person.id), "full_name": person.full_name}
            self.client.index(index="persons", id=str(person.id), body=doc, refresh=True)
            logger.info(f"Персона индексирована: {person.full_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка индексации персоны {person.id}: {e}")
            return False

    def index_genre(self, genre: Genre) -> bool:
        """Индексирует жанр в Elasticsearch"""
        try:
            doc = {"id": str(genre.id), "name": genre.name, "description": genre.description or ""}
            self.client.index(index="genres", id=str(genre.id), body=doc, refresh=True)
            logger.info(f"Жанр индексирован: {genre.name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка индексации жанра {genre.id}: {e}")
            return False

    def delete_filmwork(self, filmwork_id: UUID) -> bool:
        """Удаляет фильм из Elasticsearch"""
        try:
            self.client.delete(index="movies", id=str(filmwork_id), refresh=True)
            logger.info(f"Фильм удалён из индекса: {filmwork_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления фильма {filmwork_id}: {e}")
            return False

    def delete_genre(self, genre_id: UUID) -> bool:
        """Удаляет жанр из Elasticsearch"""
        try:
            self.client.delete(index="genres", id=str(genre_id), refresh=True)
            logger.info(f"Жанр удалён из индекса: {genre_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления жанра {genre_id}: {e}")
            return False

    def delete_person(self, person_id: UUID) -> bool:
        """Удаляет персону из Elasticsearch"""
        try:
            self.client.delete(index="persons", id=str(person_id), refresh=True)
            logger.info(f"Персона удалена из индекса: {person_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления персоны {person_id}: {e}")
            return False

    def _filmwork_to_document(self, filmwork: Filmwork) -> dict[str, Any]:
        """Преобразует Django модель Filmwork в документ Elasticsearch"""
        # Получаем связанные данные
        genres = list(filmwork.genres.all())
        persons = filmwork.personfilmwork_set.select_related('person').all()

        # Группируем персон по ролям
        actors = []
        directors = []
        writers = []

        for pf in persons:
            person_data = {"id": str(pf.person.id), "name": pf.person.full_name}
            if pf.role == 'actor':
                actors.append(person_data)
            elif pf.role == 'director':
                directors.append(person_data)
            elif pf.role == 'writer':
                writers.append(person_data)

        return {
            "id": str(filmwork.id),
            "title": filmwork.title,
            "description": filmwork.description or "",
            "rating": filmwork.rating or 0.0,
            "release_date": filmwork.release_date.isoformat() if filmwork.release_date else None,
            "type": filmwork.type,
            "age_rating": filmwork.age_rating,
            "genres": [genre.name for genre in genres],
            "actors": actors,
            "directors": directors,
            "writers": writers,
            "actors_names": [p["name"] for p in actors],
            "directors_names": [p["name"] for p in directors],
            "writers_names": [p["name"] for p in writers],
        }


# Синглтон экземпляр
elastic_service = ElasticsearchService()
