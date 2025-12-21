from uuid import UUID

from pydantic import BaseModel, Field


class CustomBaseModel(BaseModel):
    class Config:
        populate_by_name = True


class UUIDMixin(CustomBaseModel):
    id: UUID = Field(alias='uuid')
