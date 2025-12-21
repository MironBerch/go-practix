from typing import Any

from django.core.management.base import BaseCommand

from movies.elastic import ElasticsearchStartUpService


class Command(BaseCommand):

    def handle(self, *args: Any, **kwargs: Any) -> None:
        elastic = ElasticsearchStartUpService()
        elastic.create_indices()
