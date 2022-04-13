from databases import Database
from pydantic import EmailStr
from fastapi import HTTPException, status

from app.schemas.user import UserCreate, UserInDB
from .core import BaseCrud
from app.services import auth_service

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
    INSERT INTO users (username, email, password, salt)
    VALUES (:username, :email, :password, :salt)
    RETURNING id, username, email, password, salt,
        is_active, is_superuser, created_at, updated_at;
"""


class UserCrud(BaseCrud):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_users(self, page: int = 1) -> UserInDB:
        (limit, offset) = self._get_limit_offset_from_page(page)
        user_records = await self.db.fetch_all(
            query=GET_USERS_QUERY,
            values={
                "limit": limit,
                "offset": offset
            }
        )

        if not user_records:
            return []

        return [UserInDB(**user_record) for user_record in user_records]

    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_EMAIL_QUERY,
            values={"email": email}
        )

        if not user_record:
            return None

        return UserInDB(**user_record)

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_USERNAME_QUERY,
            values={"username": username}
        )

        if not user_record:
            return None

        return UserInDB(**user_record)

    async def create_new_user(self, *, new_user: UserCreate) -> UserInDB:
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
        created_user = await self.db.fetch_one(
            query=CREATE_NEW_USER_QUERY,
            values={**new_user_params.dict()}
        )

        return UserInDB(**created_user)
