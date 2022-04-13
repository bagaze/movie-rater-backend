from typing import Callable

from app.proxy.deps import client_session
from app.db.deps import db_session


def create_start_app_handler() -> Callable:
    async def start_app() -> None:
        client_session.start()
        await db_session.start()
    return start_app


def create_stop_app_handler() -> Callable:
    async def stop_app() -> None:
        await client_session.stop()
        await db_session.stop()
    return stop_app
