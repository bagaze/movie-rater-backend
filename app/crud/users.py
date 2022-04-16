from collections import UserList
from typing import Optional
from databases import Database
from pydantic import EmailStr
from fastapi import HTTPException, status
import logging

from app.schemas.user import UserCreate, UserInDB
from .core import BaseCrud
from app.services import auth_service

logger = logging.getLogger(__name__)

COUNT_USERS_QUERY = """
    SELECT COUNT(*)
    FROM users;
"""

GET_USERS_QUERY = """
    SELECT id, username, email, password, salt,
        is_active, is_superuser, created_at, updated_at
    FROM users
    LIMIT :limit OFFSET :offset;
"""

GET_USER_BY_EMAIL_QUERY = """
    SELECT id, username, email, password, salt,
        is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE email = :email;
"""

GET_USER_BY_USERNAME_QUERY = """
    SELECT id, username, email, password, salt,
        is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE username = :username;
"""

CREATE_NEW_USER_QUERY = """
    INSERT INTO users (username, email, password, salt, is_superuser)
    VALUES (:username, :email, :password, :salt, :is_superuser)
    RETURNING id, username, email, password, salt,
        is_active, is_superuser, created_at, updated_at;
"""


class UserCrud(BaseCrud):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_users(self, *, page: int = 1) -> UserList:
        return await self._get_list_results(
            query=GET_USERS_QUERY,
            count_query=COUNT_USERS_QUERY,
            page=page,
            ResultClass=UserInDB
        )

    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        return await self._get_single_result(
            query=GET_USER_BY_EMAIL_QUERY,
            ResultClass=UserInDB,
            email=email
        )

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        return await self._get_single_result(
            query=GET_USER_BY_USERNAME_QUERY,
            ResultClass=UserInDB,
            username=username
        )

    async def _prepare_new_user(
        self,
        *,
        new_user: UserCreate
    ) -> UserCreate:

        # make sure email isn't already taken
        if await self.get_user_by_email(email=new_user.email):
            detail = "That email is already taken. " \
                "Login with that email or register with another one."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )

        # make sure username isn't already taken
        if await self.get_user_by_username(username=new_user.username):
            detail = "That username is already taken. Please try another one."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )

        user_password_update = self.auth_service.create_salt_and_hashed_password(
            plaintext_password=new_user.password
        )
        new_user_params = new_user.copy(update=user_password_update.dict())

        return new_user_params

    async def create_new_user(
        self,
        *,
        new_user: UserCreate,
        is_superuser: bool = False
    ) -> UserInDB:
        new_user_params = await self._prepare_new_user(new_user=new_user)
        created_user = await self.db.fetch_one(
            query=CREATE_NEW_USER_QUERY,
            values={
                **new_user_params.dict(),
                'is_superuser': is_superuser
            }
        )

        return UserInDB(**created_user)

    async def authenticate_user(
        self,
        *,
        email: EmailStr,
        password: str
    ) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email=email)
        logger.debug(f'get_user_by_email: user is {user}')
        if not user:
            return None
        if not self.auth_service.verify_password(
            password=password,
            salt=user.salt,
            hashed_pw=user.password,
        ):
            return None

        return user
