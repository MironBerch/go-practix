from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import CollectionInvalid

from core.config import settings
from core.enums import MongoCollections

mongo: AsyncIOMotorDatabase

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


async def create_users_collection() -> None:
    try:
        await mongo.create_collection(
            name=MongoCollections.users.name,
            validator={
                '$jsonSchema': collection_schemas[MongoCollections.users.name],
            },
        )
    except CollectionInvalid:
        pass


async def create_filmworks_collection() -> None:
    try:
        await mongo.create_collection(
            name=MongoCollections.filmworks.name,
            validator={
                '$jsonSchema': collection_schemas[MongoCollections.filmworks.name],
            },
        )
    except CollectionInvalid:
        pass


async def create_reviews_collection() -> None:
    try:
        await mongo.create_collection(
            name=MongoCollections.reviews.name,
            validator={
                '$jsonSchema': collection_schemas[MongoCollections.reviews.name],
            },
        )
    except CollectionInvalid:
        pass
    await mongo[MongoCollections.reviews.name].create_index(
        [('author_id', 1), ('filmwork_id', 1)],
        unique=True,
    )


async def start() -> None:
    global mongo
    mongo = AsyncIOMotorDatabase(
        name='ugc_database',
        client=AsyncIOMotorClient(
            host=settings.mongo.host,
            port=settings.mongo.port,
            username=settings.mongo.username,
            password=settings.mongo.password,
            uuidRepresentation='standard',
        ),
    )
    await create_users_collection()
    await create_filmworks_collection()
    await create_reviews_collection()


async def stop() -> None:
    mongo.client.close()


async def get_mongo() -> AsyncIOMotorDatabase:
    return mongo
