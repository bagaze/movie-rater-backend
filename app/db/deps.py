from databases import Database
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class DBSession:
    db_session = Database(settings.DATABASE_URL, min_size=2, max_size=10)

    async def start(self):
        logger.info(f"--- Connecting to {settings.DATABASE_URL} ---")
        try:
            await self.db_session.connect()
        except Exception as e:
            logger.warn("--- DB CONNECTION ERROR ---")
            logger.warn(e)
            logger.warn("--- DB CONNECTION ERROR ---")

    async def stop(self):
        try:
            await self.db_session.disconnect()
        except Exception as e:
            logger.warn("--- DB DISCONNECT ERROR ---")
            logger.warn(e)
            logger.warn("--- DB DISCONNECT ERROR ---")

    def __call__(self) -> Database:
        assert self.db_session is not None
        return self.db_session


db_session = DBSession()
