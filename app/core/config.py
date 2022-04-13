from pydantic import BaseSettings, validator
from starlette.datastructures import Secret  # noqa: F401
from typing import Any


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str
    TMDB_API_BASEURL: str = 'https://api.themoviedb.org'
    TMDP_API_V3: str = '/3'
    TMDB_API_KEY: str

    CHANGE_ME: str = 'CHANGEME'

    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_SERVER: str = 'db'
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = 'postgres'

    DATABASE_URL: str | None = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_uri(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return 'postgresql://' \
            f'{values.get("POSTGRES_USER")}:' \
            f'{values.get("POSTGRES_PASSWORD")}@{values.get("POSTGRES_SERVER")}:' \
            f'{values.get("POSTGRES_PORT")}/{values.get("POSTGRES_DB")}'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
