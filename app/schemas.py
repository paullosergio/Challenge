from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: Annotated[str, Field(description='Username', example='paulo', max_length=50)]
    email: Annotated[
        EmailStr,
        Field(description='Email', example='paulo@gmail.com', max_length=50),
    ]
    password: Annotated[str, Field(description='Password', example='9abdb729e4bb358a')]
    cpf: Annotated[
        Optional[str],
        Field(None, description='CPF', example='11111111111', max_length=11, pattern=r'^\d{11}$'),
    ]


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
    state: Annotated[TodoState, Field(description='State', example='Draft', max_length=50)]


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
