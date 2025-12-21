from uuid import UUID

from bson.binary import Binary
from pymongo import MongoClient


def to_binary(value: UUID) -> Binary:
    """Convert `UUID` to MongoDB binary format."""
    return Binary(value.bytes)


def create_user_by_id(mongo: MongoClient, user_id: UUID):
    user_document = {
        '_id': to_binary(user_id),
        'bookmarks': [],
    }
    mongo['ugc_database']['users'].insert_one(user_document)
