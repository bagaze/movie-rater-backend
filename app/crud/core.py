from databases import Database


class BaseCrud:
    PAGE_SIZE = 20

    def __init__(self, db: Database) -> None:
        self.db = db

    def _get_limit_offset_from_page(self, page: int) -> tuple[int, int]:
        return (self.PAGE_SIZE, self.PAGE_SIZE * (page - 1))
