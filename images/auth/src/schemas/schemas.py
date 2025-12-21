from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str


class SignUpSchema(BaseModel):
    email: str
    password: str


class SignInSchema(SignUpSchema):
    pass


class PasswordChangeSchema(BaseModel):
    old_password: str
    new_password: str


class EmailSchema(BaseModel):
    email: str


class UserSessionSchema(BaseModel):
    user_id: str
    user_agent: str
    event_date: datetime
    user_device_type: str
