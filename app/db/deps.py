from databases import Database
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class DBSession:

    def __init__(self):
        self.DB_URL = None
        if os.environ.get("TESTING"):
            self.DB_URL = f"{settings.DATABASE_URL}_test"
        else:
            self.DB_URL = settings.DATABASE_URL
        self.db_session = Database(self.DB_URL, min_size=2, max_size=10)

    async def start(self):
        logger.warning(f"--- Connecting to {settings.DATABASE_URL} ---")
        try:
            await self.db_session.connect()
        except Exception as e:
            logger.warning("--- DB CONNECTION ERROR ---")
            logger.warning(e)
            logger.warning("--- DB CONNECTION ERROR ---")

    async def stop(self):
        try:
            await self.db_session.disconnect()
        except Exception as e:
            logger.warning("--- DB DISCONNECT ERROR ---")
            logger.warning(e)
            logger.warning("--- DB DISCONNECT ERROR ---")

    def __call__(self) -> Database:
        assert self.db_session is not None
        return self.db_session


db_session = DBSession()
