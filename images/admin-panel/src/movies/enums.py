from django.db import models


class FilmworkType(models.TextChoices):
    """Тип кинопроизведения."""

    MOVIE = 'movie', 'movie'
    TV_SHOW = 'tv_show', 'tv show'


class FilmworkAgeRating(models.TextChoices):
    """Возрастной рейтинг кинопроизведения."""

    GENERAL = 'G', 'G: General audience'
    PARENTAL_GUIDANCE = 'PG', 'PG: Parental guidance suggested'
    PARENTS = 'PG-13', 'PG-13: Parents cautioned'
    RESTRICTED = 'R', 'R: Restricted'
    ADULTS = 'NC-17', 'NC-17: Adults only'


class FilmworkAccessType(models.TextChoices):
    """Тип доступа к кинопроизведению."""

    PUBLIC = 'public'
    SUBSCRIPTION = 'subscription'


class PersonRole(models.TextChoices):
    """Роль персоны."""

    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'
