from typing import Any

from redis.asyncio import Redis

redis: Redis


class RedisAdapter:
    def __init__(self, redis_instance: Redis):
        self.redis = redis_instance

    async def get_object_from_cache(self, redis_key: str) -> Any:
        data = await self.redis.get(redis_key)
        if not data:
            return None
        return data

    async def put_object_to_cache(self, redis_key: str, object: Any, ex: int | None = None) -> None:
        await self.redis.set(redis_key, object, ex=ex)


async def get_redis_adapter() -> RedisAdapter:
    return RedisAdapter(redis_instance=redis)
