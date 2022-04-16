from typing import Tuple
import math
from databases import Database

from app.schemas.core import CoreModel, ListResult


class BaseCrud:
    PAGE_SIZE = 20

    def __init__(self, db: Database) -> None:
        self.db = db

    def _get_limit_offset_from_page(self, page: int) -> tuple[int, int]:
        return (self.PAGE_SIZE, self.PAGE_SIZE * (page - 1))

    async def _get_total_results_and_pages(self, *, count_query: str) -> Tuple[int, int]:
        total_results = await self.db.fetch_val(
            query=count_query
        )
        total_pages = math.ceil(total_results / self.PAGE_SIZE)

        return (total_results, total_pages)

    async def _get_list_results(
        self,
        *,
        query: str,
        count_query: str,
        page: int,
        ResultClass: CoreModel,
        **query_params
    ) -> ListResult:
        (limit, offset) = self._get_limit_offset_from_page(page)
        records = await self.db.fetch_all(
            query=query,
            values={
                "limit": limit,
                "offset": offset,
                **query_params
            }
        )

        (total_results, total_pages) = \
            await self._get_total_results_and_pages(count_query=count_query)

        results = {
            'page': page,
            'total_results': total_results,
            'total_pages': total_pages,
            'results': [ResultClass(**record)
                        for record in records]
        }

        return results

    async def _get_single_result(
        self,
        *,
        query: str,
        ResultClass: CoreModel,
        **query_params
    ) -> CoreModel:
        record = await self.db.fetch_one(
            query=query,
            values={**query_params}
        )

        if not record:
            return None

        return ResultClass(**record)
