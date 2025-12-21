from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseService(ABC):
    def __init__(self, mongo: AsyncIOMotorDatabase) -> None:
        self.mongo = mongo

    @abstractmethod
    def get(self) -> None:
        pass

    @abstractmethod
    def filter(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def remove(self) -> None:
        pass

    @abstractmethod
    def get_rating(self) -> None:
        pass

    @abstractmethod
    def rate(self) -> None:
        pass

    @abstractmethod
    def unrate(self) -> None:
        pass
