from typing import Any

from django.core.management.base import BaseCommand

from movies.mongo import MongoDBStartUpService


class Command(BaseCommand):

    def handle(self, *args: Any, **kwargs: Any) -> None:
        mongo = MongoDBStartUpService()
        mongo.start()
        # mongo.stop()
