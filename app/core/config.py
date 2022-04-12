from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str
    TMDB_API_BASEURL: str = 'https://api.themoviedb.org'
    TMDP_API_V3: str = '/3'
    TMDB_API_KEY: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
