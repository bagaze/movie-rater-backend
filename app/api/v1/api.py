from fastapi import APIRouter

from app.api.v1.endpoints import movies, weekly_movies, users

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(weekly_movies.router, prefix="/weekly_movies", tags=["weekly_movies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
