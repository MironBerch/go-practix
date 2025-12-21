from uuid import UUID

from pydantic import Field

from models.base import UUIDMixin


class BasePerson(UUIDMixin):
    """Базовая модель персоны."""

    full_name: str = Field(alias='name')


class Person(BasePerson):
    """Модель персоны."""

    roles: list[str]
    filmwork_ids: list[UUID]
