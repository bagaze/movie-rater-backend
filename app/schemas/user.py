from typing import Optional
from pydantic import EmailStr, constr

from app.schemas.core import DateTimeModelMixin, IDModelMixin, CoreModel


class UserBase(CoreModel):
    """
    Leaving off password and salt from base model
    """
    email: Optional[EmailStr]
    username: Optional[str]
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(CoreModel):
    """
    Email, username, and password are required for registering a new user
    """
    email: EmailStr
    username: constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")  # noqa: F722
    password: constr(min_length=5, max_length=100)


class UserUpdate(CoreModel):
    """
    Users are allowed to update their email and/or username
    """
    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")]  # noqa: F722


class UserPasswordUpdate(CoreModel):
    """
    Users can change their password
    """
    password: constr(min_length=5, max_length=100)
    salt: str


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    """
    Add in id, created_at, updated_at, and user's password and salt
    """
    password: constr(min_length=5, max_length=100)
    salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    pass
