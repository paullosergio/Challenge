from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import Message, UserList, UserPublic, UserSchema, UserUpdate
from app.security import get_current_user, get_password_hash, validate_cpf

router = APIRouter(prefix='/users', tags=['Users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    """
    Creates a new user in the database.

    Args:

        user (UserSchema): The schema containing the
        details of the user to be created.

    Raises:

        HTTPException: If the username or email already exists in the database.

    Returns:

        UserPublic: The created user with public details.
    """

    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )
    is_valid_cpf = validate_cpf(user.cpf)
    if not is_valid_cpf:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid CPF',
        )

    db_user = User(
        username=user.username, email=user.email, password=get_password_hash(user.password), cpf=user.cpf
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session: T_Session):
    """
    Retrieves a user by their unique identifier.

    Args:

        user_id (int): The unique identifier of the user to retrieve.

    Raises:

        HTTPException: If the user with the specified ID does not exist.

    Returns:

        UserPublic: The details of the retrieved user.
    """

    if db_user := session.scalar(select(User).where(User.id == user_id)):
        return db_user
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@router.get('/', response_model=UserList)
def read_users(session: T_Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of users from the database with optional pagination.

    Args:

        skip (int, optional): The number of users to skip before starting to collect the result set.
        limit (int, optional): The maximum number of users to return.

    Returns:

        UserList: A dictionary containing the list
        of users retrieved from the database.
    """

    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: T_Session,
    current_user: T_CurrentUser,
):
    """
    Updates the details of a specified user.

    Args:

        user_id (int): The unique identifier of the user to update.

    Raises:

        HTTPException: If the authenticated user does not have permission to update the specified user.

    Returns:

        UserPublic: The updated user details.
    """

    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    """
    Deletes a specified user from the database.

    Args:

        user_id (int): The unique identifier of the user to delete.

    Raises:

        HTTPException: If the authenticated user does not have permission to delete the specified user.

    Returns:

        Message: A confirmation message indicating
        that the user has been deleted.
    """

    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
