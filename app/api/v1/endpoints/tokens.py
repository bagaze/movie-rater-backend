from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from databases import Database
import logging

from app.schemas.token import AccessToken
from app.db.deps import db_session
from app.crud.users import UserCrud

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/",
    name="tokens:post-token",
    include_in_schema=False,
    response_model=AccessToken,
    status_code=HTTP_201_CREATED
)
@router.post(
    "",
    name="tokens:post-token",
    include_in_schema=True,
    response_model=AccessToken,
    status_code=HTTP_201_CREATED
)
async def post_token(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db_session: Database = Depends(db_session)
) -> AccessToken:
    user_crud = UserCrud(db_session)
    authenticated_user = await user_crud.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )
    logger.debug(f'authenticated user is: {authenticated_user}')
    if not authenticated_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Authentication was unsuccessful. Please verify username and password',
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = AccessToken(
        access_token=user_crud.auth_service.create_access_token_for_user(
            user=authenticated_user
        )
    )

    return access_token
