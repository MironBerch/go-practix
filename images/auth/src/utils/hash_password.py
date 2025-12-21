import hashlib
import hmac

from src.core.config import settings


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием HMAC и секретного ключа."""
    hmac_hash = hmac.new(
        settings.fastapi.secret_key.get_secret_value().encode('utf-8'),
        password.encode('utf-8'),
        hashlib.sha256,
    )
    return hmac_hash.hexdigest()


def check_password(stored_hash: str, password: str) -> bool:
    """Проверяет, соответствует ли предоставленный пароль хранящемуся хешу."""
    return stored_hash == hash_password(password)
