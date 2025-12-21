from enum import Enum


class MongoCollections(Enum):
    """Коллекций в MongoDB."""

    users = 'users'
    filmworks = 'filmworks'
    reviews = 'reviews'
