from databases import Database
from fastapi import Depends, APIRouter
from starlette.status import HTTP_201_CREATED

from app.schemas.user import UserCreate, UserPublic
from app.crud.users import UserCrud
from app.db.deps import db_session


router = APIRouter()


@router.post(
    "/",
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
    "/",
    response_model=list[UserPublic],
)
async def get_users(
    page: int = 1,
    db_session: Database = Depends(db_session)
) -> UserPublic:
    user_crud = UserCrud(db_session)
    created_users = await user_crud.get_users(page)

    return created_users
