from datetime import date
from typing import Any
from fastapi import APIRouter, Depends
import aiohttp

from app.proxy import tmdb_api
from app.proxy.deps import client_session
from app.schemas import movie

router = APIRouter()


@router.get('/', include_in_schema=False, response_model=movie.MovieResult)
@router.get('', include_in_schema=True, response_model=movie.MovieResult)
async def get_weekly_movies(
    *,
    release_date_gte: date,
    release_date_lte: date,
    page: int | None = 1,
    client_session: aiohttp.ClientSession = Depends(client_session)
) -> Any:
    (_, res) = await tmdb_api.fetch_tmdb_api(
        endpoint='/discover/movie',
        client_session=client_session,
        params={
            'release_date.gte': str(release_date_gte),
            'release_date.lte': str(release_date_lte),
            'page': page
        }
    )
    return res
