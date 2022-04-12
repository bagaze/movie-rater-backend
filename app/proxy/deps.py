import aiohttp
import asyncio

from app.core.config import settings


class HttpClientSession:
    session: aiohttp.ClientSession = None

    def start(self):
        headers = {
            'Authorization': f'Bearer {settings.TMDB_API_KEY}'
        }
        self.session = aiohttp.ClientSession(
            headers=headers,
            base_url=settings.TMDB_API_BASEURL
        )

    async def stop(self):
        await self.session.close()
        # See: https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        await asyncio.sleep(0)

        self.session = None

    def __call__(self) -> aiohttp.ClientSession:
        assert self.session is not None
        return self.session


client_session = HttpClientSession()
