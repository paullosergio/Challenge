from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Todo, User
from app.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix='/todos', tags=['To-dos'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(todo: TodoSchema, user: CurrentUser, session: Session):
    """
    Creates a new todo item in the database.

    Args:

        todo (TodoSchema): The schema containing
        the details of the todo item to be created.

    Returns:

        The created todo item with public details.
    """

    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(  # noqa
    session: Session,
    user: CurrentUser,
    title: str | None = None,
    description: str | None = None,
    state: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    """
    Lists todos for the authenticated user with optional filtering.

    Args:

        title (str, optional): A substring to filter todos by title.
        description (str,optional): A substring to filter todos by description.
        state (str, optional): The state to filter todos.
        offset (int, optional): The number of items to
        skip before starting to collect the result set.
        limit (int, optional): The maximum number of items to return.

    Returns:

        TodoList: A dictionary containing the list of todos for the user.
    """

    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))

    if description:
        query = query.filter(Todo.description.contains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    """
    Deletes a specified todo item for the authenticated user.


    Args:

        todo_id (int): The unique identifier of the todo item to delete.

    Raises:

        HTTPException: If the todo item with the specified ID does not exist.

    Returns:

        Message: A confirmation message indicating
        successful deletion of the todo item.
    """

    todo = session.scalar(select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    session.delete(todo)
    session.commit()

    return {'message': 'Task has been deleted successfully.'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def patch_todo(todo_id: int, session: Session, user: CurrentUser, todo: TodoUpdate):
    db_todo = session.scalar(select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id))

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
