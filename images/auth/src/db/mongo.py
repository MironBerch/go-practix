from os import environ

from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

mongo: MongoClient

collection_schemas = {
    'users': {
        'bsonType': 'object',
        'required': ['_id', 'bookmarks'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'bookmarks': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'object',
                    'required': ['filmwork_id'],
                    'properties': {
                        'filmwork_id': {'bsonType': 'binData'},
                    },
                },
            },
        },
    },
    'filmworks': {
        'bsonType': 'object',
        'required': ['_id', 'rating'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'rating': {
                'bsonType': 'object',
                'required': ['votes'],
                'properties': {
                    'votes': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['user_id', 'score'],
                            'properties': {
                                'user_id': {'bsonType': 'binData'},
                                'score': {'bsonType': 'number'},
                            },
                        },
                    },
                },
            },
        },
    },
    'reviews': {
        'bsonType': 'object',
        'required': ['_id', 'rating'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'author_id': {'bsonType': 'binData'},
            'filmwork_id': {'bsonType': 'binData'},
            'pub_date': {'bsonType': 'date'},
            'rating': {
                'bsonType': 'object',
                'required': ['votes'],
                'properties': {
                    'votes': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['user_id', 'score'],
                            'properties': {
                                'user_id': {'bsonType': 'binData'},
                                'score': {'bsonType': 'number'},
                            },
                        },
                    },
                },
            },
        },
    },
}


def create_users_collection() -> None:
    try:
        mongo['ugc_database'].create_collection(
            name='users',
            validator={
                '$jsonSchema': collection_schemas['users'],
            },
        )
    except CollectionInvalid:
        pass


def create_filmworks_collection() -> None:
    try:
        mongo['ugc_database'].create_collection(
            name='filmworks',
            validator={
                '$jsonSchema': collection_schemas['filmworks'],
            },
        )
    except CollectionInvalid:
        pass


def start() -> None:
    global mongo
    mongo = MongoClient(
        host=environ.get('MONGO_HOST', 'mongo'),
        port=int(environ.get('MONGO_PORT', 27017)),
        username=environ.get('MONGO_USERNAME', None),
        password=environ.get('MONGO_PASSWORD', None),
        uuidRepresentation='standard',
    )
    create_users_collection()
    create_filmworks_collection()


def stop() -> None:
    mongo.client.close()


def get_mongo() -> MongoClient:
    return mongo
