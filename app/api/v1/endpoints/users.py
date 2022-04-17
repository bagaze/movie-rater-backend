from databases import Database
from fastapi import Depends, APIRouter
from starlette.status import HTTP_201_CREATED
import logging

from app.schemas.user import UserCreate, UserInDB, UserPublic, UserResult
from app.crud.users import UserCrud
from app.db.deps import db_session
from app.api.dependencies import auth

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    name="users:post-user",
    include_in_schema=False,
    response_model=UserPublic,
    status_code=HTTP_201_CREATED
)
@router.post(
    "",
    name="users:post-user",
    include_in_schema=True,
    response_model=UserPublic,
    status_code=HTTP_201_CREATED
)
async def post_user(
    new_user: UserCreate,
    db_session: Database = Depends(db_session)
) -> UserPublic:
    user_crud = UserCrud(db_session)
    created_user = await user_crud.create_new_user(new_user=new_user)

    return created_user


@router.get(
    "/me",
    name="users:get-user-me",
    include_in_schema=True,
    response_model=UserPublic,
)
async def get_user_me(
    current_user: UserInDB = Depends(auth.get_current_active_user)
) -> UserPublic:
    return current_user


@router.get(
    "/{user_id}",
    name="users:get-user-id",
    include_in_schema=True,
    response_model=UserPublic,
)
async def get_user_id(
    user_id: int,
    db_session: Database = Depends(db_session)
) -> UserPublic:
    user_crud = UserCrud(db_session)
    user = await user_crud.get_user_by_id(user_id=user_id)

    return user


@router.get(
    "/",
    name="users:get-users",
    include_in_schema=False,
    response_model=UserResult,
)
@router.get(
    "",
    name="users:get-users",
    include_in_schema=True,
    response_model=UserResult,
)
async def get_users(
    page: int = 1,
    db_session: Database = Depends(db_session),
    _: UserInDB = Depends(auth.get_current_active_admin_user)
) -> UserResult:
    user_crud = UserCrud(db_session)
    user_list = await user_crud.get_users(page=page)

    return user_list
