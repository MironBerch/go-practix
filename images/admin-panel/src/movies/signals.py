from typing import Type

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from movies.elastic import elastic_service
from movies.models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork
from movies.mongo import MongoDBService


def sync_update_filmwork(filmwork_id) -> None:
    """Обновление фильма в Elasticsearch"""
    try:
        filmwork = Filmwork.objects.prefetch_related('genres', 'personfilmwork_set__person').get(
            id=filmwork_id
        )
        elastic_service.index_filmwork(filmwork)
    except Filmwork.DoesNotExist:
        ...
    except Exception as e:
        ...


@receiver(post_save, sender=Filmwork)
def filmwork_saved(sender: Type[Filmwork], instance: Filmwork, created: bool, **kwargs) -> None:
    """При сохранении фильма"""
    if created:
        mongo_service = MongoDBService()
        mongo_service.create_filmwork_by_id(instance.id)
        elastic_service.index_filmwork(instance)
    sync_update_filmwork(instance.id)


@receiver(post_delete, sender=Filmwork)
def filmwork_deleted(sender: Type[Filmwork], instance: Filmwork, **kwargs) -> None:
    """При удалении фильма"""
    mongo_service = MongoDBService()
    mongo_service.delete_filmwork_cascade_by_id(instance.id)
    elastic_service.delete_filmwork(instance.id)


@receiver(post_save, sender=Person)
def person_saved(sender: Type[Person], instance: Person, created: bool, **kwargs) -> None:
    """При сохранении персоны"""
    elastic_service.index_person(instance)
    filmwork_ids = Filmwork.objects.filter(persons=instance).values_list('id', flat=True)
    for filmwork_id in filmwork_ids:
        sync_update_filmwork(filmwork_id)


@receiver(pre_delete, sender=Genre)
def genre_pre_delete(sender: Type[Genre], instance: Genre, **kwargs) -> None:
    """Сохраняем информацию о связанных фильмах перед удалением жанра"""
    instance._filmwork_ids = list(
        Filmwork.objects.filter(genres=instance).values_list('id', flat=True)
    )


@receiver(post_delete, sender=Genre)
def genre_deleted(sender: Type[Genre], instance: Genre, **kwargs) -> None:
    """При удалении жанра"""
    try:
        # Удаляем жанр из Elasticsearch
        elastic_service.client.delete(index="genres", id=str(instance.id), refresh=True)
    except Exception:
        ...
    filmwork_ids = getattr(instance, '_filmwork_ids', [])
    for filmwork_id in filmwork_ids:
        sync_update_filmwork(filmwork_id)


@receiver(pre_delete, sender=Person)
def person_pre_delete(sender: Type[Person], instance: Person, **kwargs) -> None:
    """Сохраняем информацию о связанных фильмах перед удалением персоны"""
    instance._filmwork_ids = list(
        Filmwork.objects.filter(persons=instance).values_list('id', flat=True)
    )


@receiver(post_delete, sender=Person)
def person_deleted(sender: Type[Person], instance: Person, **kwargs) -> None:
    """При удалении персоны"""
    try:
        elastic_service.client.delete(index="persons", id=str(instance.id), refresh=True)
    except Exception as e:
        ...
    filmwork_ids = getattr(instance, '_filmwork_ids', [])
    for filmwork_id in filmwork_ids:
        sync_update_filmwork(filmwork_id)


@receiver(post_save, sender=Genre)
def genre_saved(sender: Type[Genre], instance: Genre, created: bool, **kwargs) -> None:
    """При сохранении жанра"""
    elastic_service.index_genre(instance)
    filmwork_ids = Filmwork.objects.filter(genres=instance).values_list('id', flat=True)

    for filmwork_id in filmwork_ids:
        sync_update_filmwork(filmwork_id)


@receiver(post_save, sender=GenreFilmwork)
@receiver(post_delete, sender=GenreFilmwork)
def genrefilmwork_changed(sender: Type[GenreFilmwork], instance: GenreFilmwork, **kwargs) -> None:
    """При изменении связи фильм-жанр"""
    sync_update_filmwork(instance.film_work.id)


@receiver(post_save, sender=PersonFilmwork)
@receiver(post_delete, sender=PersonFilmwork)
def personfilmwork_changed(
    sender: Type[PersonFilmwork], instance: PersonFilmwork, **kwargs
) -> None:
    """При изменении связи фильм-персона"""
    sync_update_filmwork(instance.film_work.id)
