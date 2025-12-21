from models.base import UUIDMixin


class Genre(UUIDMixin):
    """Модель жанра."""

    name: str
    description: str
