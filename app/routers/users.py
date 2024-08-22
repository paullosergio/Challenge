from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.logging_config import logger
from app.models import User
from app.schemas import Message, UserList, UserPublic, UserSchema, UserUpdate
from app.security import get_current_user, get_password_hash, validate_cpf

router = APIRouter(prefix='/users', tags=['Users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    logger.info('Attempting to create a new user with username: %s', user.username)

    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            logger.warning('Username already exists: %s', user.username)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            logger.warning('Email already exists: %s', user.email)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )
    is_valid_cpf = validate_cpf(user.cpf)
    if not is_valid_cpf:
        logger.warning('Invalid CPF: %s', user.cpf)
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

    logger.info('User created with ID: %d', db_user.id)
    return db_user


@router.get('/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session: T_Session):
    logger.info('Attempting to retrieve user with ID: %d', user_id)

    if db_user := session.scalar(select(User).where(User.id == user_id)):
        logger.info('User found with ID: %d', user_id)
        return db_user
    else:
        logger.warning('User not found with ID: %d', user_id)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@router.get('/', response_model=UserList)
def read_users(session: T_Session, skip: int = 0, limit: int = 100):
    logger.info('Retrieving users with skip=%d and limit=%d', skip, limit)

    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: T_Session,
    current_user: T_CurrentUser,
):
    logger.info('Attempting to update user with ID: %d', user_id)

    if current_user.id != user_id:
        logger.warning('Forbidden update attempt by user ID: %d', current_user.id)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    existing_user = session.scalar(
        select(User).where((User.email == user.email) | (User.username == user.username))
    )

    if existing_user:
        if existing_user.email == user.email:
            logger.warning('Email %s is already in use by another user', user.email)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Email already in use')
        if existing_user.username == user.username:
            logger.warning('Username %s is already in use by another user', user.username)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Username already in use')

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email
    session.commit()
    session.refresh(current_user)

    logger.info('User updated with ID: %d', user_id)
    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    logger.info('Attempting to delete user with ID: %d', user_id)

    if current_user.id != user_id:
        logger.warning('Forbidden delete attempt by user ID: %d', current_user.id)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    session.delete(current_user)
    session.commit()

    logger.info('User deleted with ID: %d', user_id)
    return {'message': 'User deleted'}
