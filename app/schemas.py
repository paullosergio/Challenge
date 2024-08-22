import re
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.logging_config import logger
from app.models import TodoState

MIN_LEN_PASSWORD = 8


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: Annotated[str, Field(description='Username', example='paulo', max_length=50)]
    email: Annotated[
        EmailStr,
        Field(description='Email', example='paulo@gmail.com', max_length=50),
    ]
    cpf: Annotated[
        Optional[str],
        Field(None, description='CPF', example='11111111111', max_length=11),
    ]
    password: Annotated[str, Field(description='Password', example='9abdb729e4bb358a')]

    @field_validator('password', mode='before')
    def password_length(cls, value):
        if len(value) < MIN_LEN_PASSWORD:
            logger.warning('Invalid password attempt: %s', value)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Password must be at least 8 characters long. Please enter a stronger password.',
            )
        return value

    @field_validator('cpf', mode='before')
    def validate_cpf(cls, value):
        if not re.match(r'^\d{11}$', value):
            logger.warning('Invalid CPF attempt: %s', value)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='CPF must be exactly 11 digits long.',
            )
        return value


class UserUpdate(BaseModel):
    username: Annotated[str, Field(description='Username', example='paulo', max_length=50)]
    password: Annotated[str, Field(description='Password', example='9abdb729e4bb358a')]
    email: Annotated[
        EmailStr,
        Field(description='Email', example='paulo@gmail.com', max_length=50),
    ]


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoSchema(BaseModel):
    title: Annotated[str, Field(description='Title', example='Finish report', max_length=50)]
    description: Annotated[
        str,
        Field(
            description='Description',
            example='Complete the financial report and submit it by Friday',
            max_length=150,
        ),
    ]
    state: Annotated[TodoState, Field(description='State', example='draft', max_length=10)]


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
