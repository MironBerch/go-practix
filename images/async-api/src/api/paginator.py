from fastapi import Query


class Paginator:
    def __init__(
        self,
        page_number: int = Query(
            default=1,
            alias='page[number]',
            description='Page number',
            ge=1,
        ),
        page_size: int = Query(
            default=50,
            alias='page[size]',
            description='Page size',
            ge=1,
            le=100,
        ),
    ):
        self.page = page_number
        self.size = page_size
