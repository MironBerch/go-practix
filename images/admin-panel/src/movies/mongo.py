from uuid import UUID

from bson.binary import Binary
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from config import settings


class MongoDBStartUpService:
    def __init__(self) -> None:
        self.mongo = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            username=settings.MONGO_USERNAME,
            password=settings.MONGO_PASSWORD,
            uuidRepresentation=settings.MONGO_UUID_REPRESENTATION,
        )

    def start(self) -> None:
        self._create_users_collection()
        self._create_filmworks_collection()

    def _create_users_collection(self) -> None:
        try:
            self.mongo['ugc_database'].create_collection(
                name='users',
                validator={
                    '$jsonSchema': settings.MONGO_COLLECTION_SCHEMAS['users'],
                },
            )
        except CollectionInvalid:
            ...

    def _create_filmworks_collection(self) -> None:
        try:
            self.mongo['ugc_database'].create_collection(
                name='filmworks',
                validator={
                    '$jsonSchema': settings.MONGO_COLLECTION_SCHEMAS['filmworks'],
                },
            )
        except CollectionInvalid:
            ...


class MongoDBService:
    def __init__(self) -> None:
        self.mongo = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            username=settings.MONGO_USERNAME,
            password=settings.MONGO_PASSWORD,
            uuidRepresentation=settings.MONGO_UUID_REPRESENTATION,
        )

    def create_filmwork_by_id(self, filmwork_id: UUID) -> None:
        filmwork_document = {
            '_id': self.to_binary(filmwork_id),
            'rating': {
                'votes': [],
            },
        }
        self.mongo['ugc_database']['filmworks'].insert_one(filmwork_document)

    def delete_filmwork_cascade_by_id(self, filmwork_id: UUID) -> bool:
        """Удаляет фильм и все связанные с ним данные."""
        try:
            binary_id = self.to_binary(filmwork_id)
            db = self.mongo['ugc_database']

            # 1. Удаляем фильм
            filmwork_result = db['filmworks'].delete_one({'_id': binary_id})

            if filmwork_result.deleted_count == 0:
                print(f"Фильм с ID {filmwork_id} не найден")
                return False

            # 2. Удаляем рецензии к фильму (если есть коллекция reviews)
            reviews_result = db['reviews'].delete_many({'filmwork_id': binary_id})
            print(f"Удалено рецензий: {reviews_result.deleted_count}")

            # 3. Удаляем фильм из закладок пользователей
            # Обновляем всех пользователей, удаляя этот фильм из их bookmarks
            users_result = db['users'].update_many(
                {'bookmarks.filmwork_id': binary_id},
                {'$pull': {'bookmarks': {'filmwork_id': binary_id}}},
            )
            print(f"Обновлено пользователей: {users_result.modified_count}")

            # 4. Удаляем оценки фильма из других коллекций если есть
            # Например, если оценки хранятся отдельно

            print(f"Фильм {filmwork_id} и связанные данные удалены")
            return True

        except Exception as e:
            print(f"Ошибка каскадного удаления: {e}")
            return False

    def to_binary(self, value: UUID) -> Binary:
        """Convert `UUID` to MongoDB binary format."""
        return Binary(value.bytes)
