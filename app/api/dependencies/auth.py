from typing import Optional
from databases import Database

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.schemas.user import UserInDB
from app.services import auth_service
from app.db.deps import db_session
from app.crud.users import UserCrud


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login/token/")


async def get_user_from_token(
    *,
    token: str = Depends(oauth2_scheme),
    db_session: Database = Depends(db_session),
) -> Optional[UserInDB]:
    try:
        user_crud = UserCrud(db_session)
        username = auth_service.get_username_from_token(
            token=token,
            secret_key=str(settings.SECRET_KEY)
        )
        user = await user_crud.get_user_by_username(username=username)
    except Exception as e:
        raise e

    return user


def get_current_active_user(
    current_user: UserInDB = Depends(get_user_from_token)
) -> Optional[UserInDB]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an active user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


def get_current_active_admin_user(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Optional[UserInDB]:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an super user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user
