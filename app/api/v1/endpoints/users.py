from databases import Database
from fastapi import Depends, APIRouter, Response, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
import logging

from app.schemas.user import UserCreate, UserInDB, UserPublic, UserResult, UserUpdate
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


@router.put(
    "/{user_id}",
    name="users:put-user-id",
    include_in_schema=True,
    response_model=UserPublic,
)
async def put_user_id(
    user_id: int,
    user_to_update: UserUpdate,
    db_session: Database = Depends(db_session),
    current_user: UserInDB = Depends(auth.get_current_active_user)
) -> UserPublic:
    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to modify this user."
        )
    user_crud = UserCrud(db_session)
    user = await user_crud.update_user(user_id=user_id, user_to_update=user_to_update)

    return user


@router.delete(
    "/{user_id}",
    name="users:delete-user-id",
    include_in_schema=True,
    status_code=HTTP_204_NO_CONTENT,
    response_class=Response
)
async def delete_user(
    user_id: int,
    admin: UserInDB = Depends(auth.get_current_active_admin_user),
    db_session: Database = Depends(db_session)
) -> Response:
    user_crud = UserCrud(db_session)

    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to delete yourself."
        )

    await user_crud.delete_user(user_id=user_id)
