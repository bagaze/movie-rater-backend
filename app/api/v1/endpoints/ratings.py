from fastapi import APIRouter, Depends, Response, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from databases import Database
import logging

from app.schemas.rating import (
    RatingCreate, RatingCreatePublic, RatingPublic, RatingResult, RatingUpdatePublic
)
from app.crud.ratings import RatingCrud
from app.db.deps import db_session
from app.schemas.user import UserInDB
from app.api.dependencies import auth


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    name="ratings:get-ratings",
    include_in_schema=False,
    response_model=RatingResult,
)
@router.get(
    "",
    name="ratings:get-ratings",
    include_in_schema=True,
    response_model=RatingResult,
)
async def get_ratings(
    page: int = 1,
    db_session: Database = Depends(db_session)
) -> RatingResult:
    rating_crud = RatingCrud(db_session)
    ratings = await rating_crud.get_ratings(page=page)

    return ratings


@router.get(
    "/{rating_id}",
    name="ratings:get-rating-id",
    include_in_schema=True,
    response_model=RatingPublic,
)
async def get_rating_id(
    rating_id: int = 1,
    db_session: Database = Depends(db_session)
) -> RatingPublic:
    rating_crud = RatingCrud(db_session)
    rating = await rating_crud.get_rating_per_id(rating_id=rating_id)

    return rating


@router.post(
    "/",
    name="ratings:post-rating",
    include_in_schema=False,
    response_model=RatingPublic,
    status_code=HTTP_201_CREATED
)
@router.post(
    "",
    name="ratings:post-rating",
    include_in_schema=True,
    response_model=RatingPublic,
    status_code=HTTP_201_CREATED
)
async def post_rating(
    new_public_rating: RatingCreatePublic,
    current_user: UserInDB = Depends(auth.get_current_active_user),
    db_session: Database = Depends(db_session)
) -> RatingPublic:
    logger.debug(f'connected user is: {current_user}')
    rating_crud = RatingCrud(db_session)
    new_rating = RatingCreate(
        user_id=current_user.id,
        **new_public_rating.dict()
    )
    created_rating = await rating_crud.create_new_rating(new_rating=new_rating)

    return created_rating


@router.put(
    "/{rating_id}",
    name="ratings:put-rating-id",
    include_in_schema=True,
    response_model=RatingPublic
)
async def put_rating(
    rating_id: int,
    rating_to_update: RatingUpdatePublic,
    current_user: UserInDB = Depends(auth.get_current_active_user),
    db_session: Database = Depends(db_session)
) -> RatingPublic:
    logger.debug(f'connected user is: {current_user}')
    rating_crud = RatingCrud(db_session)

    updated_rating = await rating_crud.update_rating(
        rating_id=rating_id, rating_to_update=rating_to_update
    )
    return updated_rating


@router.delete(
    "/{rating_id}",
    name="ratings:delete-rating-id",
    include_in_schema=True,
    status_code=HTTP_204_NO_CONTENT,
    response_class=Response
)
async def delete_rating(
    rating_id: int,
    current_user: UserInDB = Depends(auth.get_current_active_user),
    db_session: Database = Depends(db_session)
) -> Response:
    logger.debug(f'connected user is: {current_user}')
    rating_crud = RatingCrud(db_session)

    try:
        rating = await rating_crud.get_rating_per_id(rating_id=rating_id)
        if rating.user_id == current_user.id:
            await rating_crud.delete_rating(rating_id=rating_id)
    except HTTPException:
        pass
