from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.logging_config import logger
from app.models import User
from app.schemas import Token
from app.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['Auth'])

T_Session = Annotated[Session, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form_data: T_OAuth2Form):
    """
    Authenticates a user and issues an access token.

    Args:
        form_data (T_OAuth2Form): The form data containing the user's
        username and password.

    Raises:
        HTTPException: If the username or password is incorrect.

    Returns:
        Token: A dictionary containing the access token and its type.
    """
    logger.info('Attempting to authenticate user with username: %s', form_data.username)

    user = session.scalar(select(User).where(User.username == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        logger.warning('Authentication failed for username: %s', form_data.username)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    logger.info('Authentication successful for username: %s - Access token issued', form_data.username)

    return {'access_token': access_token, 'token_type': 'Bearer'}
