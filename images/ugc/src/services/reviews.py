from datetime import datetime
from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi import Depends

from api.paginator import Paginator
from db.mongo import get_mongo
from services.base import BaseService
from services.utils import to_binary, to_uuid


class ReviewsService(BaseService):
    async def get(self, user_id: UUID, filmwork_id: UUID):
        result = await self.mongo['reviews'].find_one(
            {'filmwork_id': to_binary(filmwork_id), 'author_id': to_binary(user_id)},
        )
        return result

    async def filter(self, filmwork_id: UUID, paginator: Paginator):
        result = (
            await self.mongo['reviews']
            .find({'filmwork_id': to_binary(filmwork_id)})
            .skip((paginator.page - 1) * paginator.size)
            .limit(paginator.size)
            .to_list(length=None)
        )
        for obj in result:
            obj['id'] = to_uuid(obj['_id'])
            obj['filmwork_id'] = to_uuid(obj['filmwork_id'])
            obj['author_id'] = to_uuid(obj['author_id'])
        return result

    async def update(self, user_id: UUID, filmwork_id: UUID, text: str):
        object_id = to_binary(uuid4())
        await self.mongo['reviews'].update_one(
            {
                'author_id': to_binary(user_id),
                'filmwork_id': to_binary(filmwork_id),
            },
            {
                '$set': {'text': text},
                '$setOnInsert': {
                    '_id': object_id,
                    'pub_date': datetime.now(),
                    'rating': {'votes': []},
                    'author_id': to_binary(user_id),
                    'filmwork_id': to_binary(filmwork_id),
                },
            },
            upsert=True,
        )
        result = await self.mongo['reviews'].find_one(
            {'filmwork_id': to_binary(filmwork_id), 'author_id': to_binary(user_id)},
        )
        result['id'] = to_uuid(result['_id'])
        result['filmwork_id'] = to_uuid(result['filmwork_id'])
        result['author_id'] = to_uuid(result['author_id'])
        return result

    async def remove(self, review_id: UUID, user_id: UUID, filmwork_id: UUID):
        await self.mongo['reviews'].delete_one(
            {
                '_id': to_binary(review_id),
                'author_id': to_binary(user_id),
                'filmwork_id': to_binary(filmwork_id),
            },
        )

    async def get_rating(self, review_id: UUID, filmwork_id: UUID):
        result = await self.mongo['reviews'].find_one(
            {
                '_id': to_binary(review_id),
                'filmwork_id': to_binary(filmwork_id),
            },
        )
        return result['rating']

    async def rate(self, review_id: UUID, user_id: UUID, filmwork_id: UUID, score: int):
        user_id_bytes = user_id.bytes
        review: dict = await self.mongo['reviews'].find_one({'_id': to_binary(review_id)})
        votes: list = review.get('rating', {}).get('votes', [])
        for vote in votes:
            if vote['user_id'] == user_id_bytes:
                vote['score'] = score
                break
        else:
            votes.append({'user_id': to_binary(user_id), 'score': score})
        result = await self.mongo['reviews'].update_one(
            {'_id': to_binary(review_id)},
            {'$set': {'rating.votes': votes}},
            upsert=True,
        )
        result = await self.mongo['reviews'].find_one(
            {
                '_id': to_binary(review_id),
                'filmwork_id': to_binary(filmwork_id),
            },
        )
        return result['rating']

    async def unrate(self, review_id: UUID, filmwork_id: UUID, user_id: UUID):
        await self.mongo['reviews'].update_one(
            {'_id': to_binary(review_id)},
            {'$pull': {'rating.votes': {'user_id': to_binary(user_id)}}},
        )
        result = await self.mongo['reviews'].find_one(
            {
                '_id': to_binary(review_id),
                'filmwork_id': to_binary(filmwork_id),
            },
        )
        return result['rating']


def get_reviews_service(
    mongo: AsyncIOMotorDatabase = Depends(get_mongo),
) -> ReviewsService:
    return ReviewsService(mongo=mongo)
