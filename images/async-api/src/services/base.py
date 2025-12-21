import json
from abc import abstractmethod
from typing import Any
from uuid import UUID

from core.utils import get_redis_key
from db.elastic import ElasticAdapter
from db.redis import RedisAdapter


class BaseListService:
    def __init__(
        self,
        db_adapter: ElasticAdapter,
        cache_adapter: RedisAdapter,
        index: str,
        model: Any,
    ):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter
        self.model = model
        self.index = index

    @staticmethod
    @abstractmethod
    def get_elastic_query(**kwargs):
        pass

    async def get_objects(
        self,
        page_size: int = 100,
        page_number: int = 1,
        **kwargs,
    ) -> list:
        query = self.get_elastic_query(**kwargs)
        redis_key = get_redis_key(self.index, query, page_size, page_number)
        objects = await self.cache_adapter.get_objects_from_cache(redis_key)
        if objects:
            objects = [self.model.model_validate_json(document) for document in json.loads(objects)]
        else:
            objects = await self.db_adapter.get_objects_from_db(
                self.index,
                self.model,
                query,
                page_size,
                page_number,
            )
            if not objects:
                return []
            json_objects = json.dumps([document.json() for document in objects])
            await self.cache_adapter.put_objects_to_cache(json_objects, redis_key)
        return objects


class RetrieveService:
    def __init__(
        self,
        db_adapter: ElasticAdapter,
        cache_adapter: RedisAdapter,
        index: str,
        model: Any,
    ):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter
        self.model = model
        self.index = index

    async def get_by_pk(self, object_pk: UUID):
        object = await self.cache_adapter.get_objects_from_cache(str(object_pk))
        if object:
            object = self.model.model_validate_json(object)
        else:
            object = await self.db_adapter.get_object_from_db(
                index=self.index,
                model=self.model,
                object_pk=str(object_pk),
            )
            if not object:
                return None
            await self.cache_adapter.put_objects_to_cache(
                redis_key=object.json(),
                objects=str(object_pk),
            )
        return object
