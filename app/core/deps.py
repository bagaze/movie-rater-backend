from typing import Callable
from fastapi import FastAPI

from app.proxy.deps import client_session
from app.db.deps import connect_to_db, close_db_connection


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        client_session.start()
        await connect_to_db(app)
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await client_session.stop()
        await close_db_connection(app)
    return stop_app
