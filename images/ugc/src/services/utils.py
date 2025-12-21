from uuid import UUID

from bson.binary import Binary


def to_binary(value: UUID) -> Binary:
    """Convert `UUID` to MongoDB binary format."""
    return Binary(value.bytes)


def to_uuid(value: bytes) -> UUID:
    """Convert MongoDB binary to `UUID`."""
    return UUID(bytes=value)
