import hashlib


def get_redis_key(
    index: str,
    query: dict,
    page_size: int,
    page_number: int,
) -> str:
    params = f'{query}{page_size}{page_number}'
    hash_string = hashlib.md5(params.encode()).hexdigest()
    return f'elastic_cache::{index}::{hash_string}'
