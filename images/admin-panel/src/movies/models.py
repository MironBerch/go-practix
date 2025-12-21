import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from movies.consts import MAX_ENUM_STRING_LEN, MAX_STRING_LEN
from movies.enums import FilmworkAccessType, FilmworkAgeRating, FilmworkType, PersonRole


class TimeStampedMixin(models.Model):
    """Абстрактый класс для отметки времени создания и модификации объектов модели."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """Абстрактый класс для генерации первичных ключей."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Жанр кинопроизведения."""

    name = models.CharField(
        max_length=MAX_STRING_LEN,
        unique=True,
    )
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'content\".\"genre'

    def __str__(self) -> str:
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Кинопроизведение."""

    title = models.CharField(max_length=MAX_STRING_LEN)
    description = models.TextField(blank=True)
    release_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
    )
    rating = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )
    access_type = models.CharField(
        max_length=MAX_ENUM_STRING_LEN,
        choices=FilmworkAccessType.choices,
        default=FilmworkAccessType.PUBLIC,
    )
    type = models.CharField(
        max_length=MAX_ENUM_STRING_LEN,
        choices=FilmworkType.choices,
        default=FilmworkType.MOVIE,
    )
    age_rating = models.CharField(
        max_length=MAX_ENUM_STRING_LEN,
        choices=FilmworkAgeRating.choices,
        default=FilmworkAgeRating.GENERAL,
    )
    genres = models.ManyToManyField(
        'Genre',
        through='GenreFilmwork',
    )
    persons = models.ManyToManyField(
        'Person',
        through='PersonFilmwork',
    )

    class Meta:
        db_table = 'content\".\"film_work'

    def __str__(self) -> str:
        return self.title


class GenreFilmwork(UUIDMixin):
    """Промежуточная таблица привязки жанров и кинопроизведений."""

    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content\".\"genre_film_work'
        unique_together = (('film_work', 'genre'),)

    def __str__(self) -> str:
        return f'{self.film_work.title} - {self.genre.name}'


class Person(UUIDMixin, TimeStampedMixin):
    """Персона съемочной группы (актер, режиссер и т.д.)."""

    full_name = models.CharField(max_length=MAX_STRING_LEN)

    class Meta:
        db_table = 'content\".\"person'

    def __str__(self) -> str:
        return self.full_name


class PersonFilmwork(UUIDMixin):
    """Промежуточная таблица для связи персонала и кинопроизведений."""

    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        choices=PersonRole.choices,
        default=PersonRole.ACTOR,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content\".\"person_film_work'
        indexes = [
            models.Index(fields=['film_work', 'person']),
        ]

    def __str__(self) -> str:
        return f'{self.film_work.title} - {self.person.full_name} - {self.role}'
