from typing import Tuple
import math
from databases import Database


class BaseCrud:
    PAGE_SIZE = 20

    def __init__(self, db: Database) -> None:
        self.db = db

    def _get_limit_offset_from_page(self, page: int) -> tuple[int, int]:
        return (self.PAGE_SIZE, self.PAGE_SIZE * (page - 1))

    async def _get_total_results_and_pages(self, *, query: str) -> Tuple[int, int]:
        total_results = await self.db.fetch_val(
            query=query
        )
        total_pages = math.ceil(total_results / self.PAGE_SIZE)

        return (total_results, total_pages)
