from typing import Any
from fastapi import APIRouter, Depends
import aiohttp

from app.proxy import tmdb_api
from app.proxy.deps import client_session
from app.schemas import movie

router = APIRouter()


@router.get('/{movie_id}', include_in_schema=True, response_model=movie.MovieDetail)
async def get_movie(
    *,
    movie_id: int,
    client_session: aiohttp.ClientSession = Depends(client_session)
) -> Any:
    (_, res) = await tmdb_api.fetch_tmdb_api(
        endpoint=f'/movie/{movie_id}',
        params={
            'append_to_response': 'credits'
        },
        client_session=client_session
    )
    return res


@router.get('/', include_in_schema=False, response_model=movie.MovieResult)
@router.get('', include_in_schema=True, response_model=movie.MovieResult)
async def get_movies(
    *,
    query: str,
    page: int | None = 1,
    client_session: aiohttp.ClientSession = Depends(client_session)
) -> Any:
    (_, res) = await tmdb_api.fetch_tmdb_api(
        endpoint='/search/movie',
        client_session=client_session,
        params={
            'query': query,
            'page': page
        }
    )
    return res
