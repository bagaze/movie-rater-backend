import aiohttp
from app.core.config import settings

DEFAULT_PARAMS = {
    'language': 'fr-FR',
    'with_release_type': '3'
}


async def fetch_tmdb_api(
        endpoint: str,
        client_session: aiohttp.ClientSession,
        params: dict = None) -> tuple[int, dict]:
    if params:
        merged_params = {
            **DEFAULT_PARAMS,
            **{k: v for k, v in params.items() if v is not None}
        }
    else:
        merged_params = DEFAULT_PARAMS
    async with client_session.get(
            f'{settings.TMDP_API_V3}{endpoint}',
            params=merged_params) as resp:
        status = resp.status
        json = await resp.json()

        return (status, json)
