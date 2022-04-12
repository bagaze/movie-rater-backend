from typing import Any
from pydantic import BaseModel


class ListResult(BaseModel):
    page: int
    results: list[Any]
    total_results: int
    total_pages: int
