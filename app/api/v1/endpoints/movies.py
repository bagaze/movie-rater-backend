from fastapi import APIRouter, Depends, status as http_status, HTTPException
from databases import Database
import aiohttp

from app.proxy import tmdb_api
from app.proxy.deps import client_session
from app.schemas import movie
from app.crud.ratings import RatingCrud
from app.db.deps import db_session

router = APIRouter()


@router.get(
    '/{movie_id}',
    name="movies:get-movie-id",
    include_in_schema=True,
    response_model=movie.MovieDetailPublic
)
async def get_movie(
    *,
    movie_id: int,
    client_session: aiohttp.ClientSession = Depends(client_session),
    db_session: Database = Depends(db_session)
) -> movie.MovieDetailPublic:
    (status, res) = await tmdb_api.fetch_tmdb_api(
        endpoint=f'/movie/{movie_id}',
        params={
            'append_to_response': 'credits,release_dates'
        },
        client_session=client_session
    )
    if status != http_status.HTTP_200_OK:
        raise HTTPException(
            status,
            detail=res['status_message']
        )

    rating_crud = RatingCrud(db_session)
    avg_rating = await rating_crud.get_avg_rating_per_movie(movie_id=movie_id)
    return {**res, 'avg_rating': avg_rating}


@router.get(
    '/',
    name="movies:get-movies",
    include_in_schema=False,
    response_model=movie.MovieResult
)
@router.get(
    '',
    name="movies:get-movies",
    include_in_schema=True,
    response_model=movie.MovieResult
)
async def get_movies(
    *,
    query: str,
    page: int | None = 1,
    client_session: aiohttp.ClientSession = Depends(client_session)
) -> movie.MovieResult:
    (status, res) = await tmdb_api.fetch_tmdb_api(
        endpoint='/search/movie',
        client_session=client_session,
        params={
            'query': query,
            'page': page
        }
    )
    if status != http_status.HTTP_200_OK:
        raise HTTPException(
            status,
            detail=res['status_message']
        )

    return res
