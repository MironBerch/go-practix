from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi import Depends

from api.paginator import Paginator
from db.mongo import get_mongo
from services.base import BaseService
from services.utils import to_binary, to_uuid


class BookmarksService(BaseService):
    async def filter(self, user_id: UUID, paginator: Paginator):
        result = (
            await self.mongo['users']
            .find({'_id': to_binary(user_id)})
            .skip((paginator.page - 1) * paginator.size)
            .limit(paginator.size)
            .to_list(length=None)
        )
        if result != []:
            result = [
                {'filmwork_id': to_uuid(bookmark['filmwork_id'])}
                for bookmark in result[0].get('bookmarks', [])
            ]
        return result

    async def update(self, user_id: UUID, filmwork_id: UUID):
        await self.mongo['users'].update_one(
            {'_id': to_binary(user_id)},
            {
                '$addToSet': {
                    'bookmarks': {
                        'filmwork_id': to_binary(filmwork_id),
                    }
                }
            },
            upsert=True,
        )
        return {'filmwork_id': filmwork_id}

    async def remove(self, user_id: UUID, filmwork_id: UUID):
        await self.mongo['users'].update_one(
            {'_id': to_binary(user_id)},
            {
                '$pull': {
                    'bookmarks': {
                        'filmwork_id': to_binary(filmwork_id),
                    }
                }
            },
        )
        return {'filmwork_id': filmwork_id}

    def get(self) -> None:
        raise NotImplementedError()

    def get_rating(self) -> None:
        raise NotImplementedError()

    def rate(self) -> None:
        raise NotImplementedError()

    def unrate(self) -> None:
        raise NotImplementedError()


def get_bookmarks_service(
    mongo: AsyncIOMotorDatabase = Depends(get_mongo),
) -> BookmarksService:
    return BookmarksService(mongo=mongo)
