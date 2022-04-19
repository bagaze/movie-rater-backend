import logging
from asyncpg import UniqueViolationError
from databases import Database
from fastapi import HTTPException, status

from app.crud.core import BaseCrud
from app.schemas.rating import RatingCreate, RatingInDB, RatingResult, RatingUpdatePublic
from app.schemas.user import UserInDB
from app.services import auth_service


logger = logging.getLogger(__name__)

COUNT_RATINGS_QUERY = """
    SELECT COUNT(*)
    FROM ratings;
"""

GET_RATINGS_QUERY = """
    SELECT id, movie_id, user_id, grade,
        created_at, updated_at
    FROM ratings
    LIMIT :limit OFFSET :offset;
"""

GET_RATINGS_BY_USER_QUERY = """
    SELECT id, movie_id, user_id, grade,
        created_at, updated_at
    FROM ratings
    WHERE user_id = :user_id
    LIMIT :limit OFFSET :offset;
"""

GET_RATING_BY_USER_MOVIE_QUERY = """
    SELECT id, movie_id, user_id, grade,
        created_at, updated_at
    FROM ratings
    WHERE user_id = :user_id AND movie_id = :movie_id;
"""

GET_RATING_BY_ID = """
    SELECT id, movie_id, user_id, grade,
        created_at, updated_at
    FROM ratings
    WHERE id = :id;
"""

CREATE_NEW_RATING_QUERY = """
    INSERT INTO ratings (movie_id, user_id, grade)
    VALUES (:movie_id, :user_id, :grade)
    RETURNING id, movie_id, user_id, grade,
        created_at, updated_at;
"""

UPDATE_RATING_QUERY = """
    UPDATE ratings
    SET movie_id = :movie_id, grade = :grade
    WHERE id = :id
    RETURNING id, movie_id, user_id, grade,
        created_at, updated_at;
"""

DELETE_RATING_QUERY = """
    DELETE FROM ratings
    WHERE id = :id;
"""


class RatingCrud(BaseCrud):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_ratings(self, *, page: int = 1) -> RatingResult:
        return await self._get_list_results(
            query=GET_RATINGS_QUERY,
            count_query=COUNT_RATINGS_QUERY,
            page=page,
            ResultClass=RatingInDB
        )

    async def get_ratings_per_user(
        self,
        *,
        current_user: UserInDB,
        page: int = 1
    ) -> RatingResult:
        return await self._get_list_results(
            query=GET_RATINGS_QUERY,
            count_query=COUNT_RATINGS_QUERY,
            page=page,
            ResultClass=RatingInDB,
            user_id=current_user.id
        )

    async def get_rating_per_id(self, *, rating_id: int) -> RatingInDB:
        rating = await self._get_single_result(
            query=GET_RATING_BY_ID,
            ResultClass=RatingInDB,
            id=rating_id
        )

        if rating is None:
            detail = f"Rating with id={rating_id} does not exist"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail
            )

        return rating

    async def get_rating_per_user_movie(
        self,
        *,
        current_user: UserInDB,
        movie_id: int
    ) -> RatingInDB:
        return await self._get_single_result(
            query=GET_RATING_BY_USER_MOVIE_QUERY,
            ResultClass=RatingInDB,
            user_id=current_user.id,
            movie_id=movie_id
        )

    async def create_new_rating(self, *, new_rating: RatingCreate) -> RatingInDB:
        try:
            created_rating = await self.db.fetch_one(
                query=CREATE_NEW_RATING_QUERY,
                values=new_rating.dict()
            )
            logger.debug(f'Created rating is {created_rating}')
        except UniqueViolationError:
            detail = "Another rating already exists"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail
            )

        return RatingInDB(**created_rating)

    async def update_rating(
        self, *, rating_id: int, rating_to_update: RatingUpdatePublic
    ) -> RatingInDB:
        updated_rating = await self.db.fetch_one(
            query=UPDATE_RATING_QUERY,
            values={
                **rating_to_update.dict(),
                'id': rating_id
            }
        )
        logger.debug(f'Updated rating is {updated_rating}')

        if updated_rating is None:
            detail = f'Rating with id={rating_id} does not exist'
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail
            )

        return RatingInDB(**updated_rating)

    async def delete_rating(
        self, *, rating_id: int
    ) -> None:
        await self.db.fetch_one(
            query=DELETE_RATING_QUERY,
            values={
                'id': rating_id
            }
        )

        return None