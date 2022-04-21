from datetime import date
from pydantic import constr, confloat, root_validator, validator, Extra

from app.schemas.core import CoreModel, IDModelMixin, ListResult


class MovieBase(CoreModel):
    original_title: str
    title: str
    vote_average: float
    vote_count: int
    poster_path: str | None
    release_date: date | None

    @validator('release_date', pre=True)
    def check_release_date(cls, v):
        if not v:
            return None
        return v


class MoviePublic(IDModelMixin, MovieBase):
    pass


class MovieDetailPublic(MoviePublic):
    imdb_id: constr(
        regex='^tt[0-9]{7}',  # noqa: F722
        min_length=9,
        max_length=9
    )
    directors: list[str] | None
    avg_rating: confloat(ge=0.0, le=10.0) | None

    @root_validator(pre=True)
    def add_directors(cls, values: dict) -> dict:
        directors = (crew_member['name']
            for crew_member in values['credits']['crew']
                if crew_member['job'] == 'Director')

        return {**values, 'directors': list(directors)}

    class Config:
        extra: Extra.allow


class MovieResult(ListResult):
    results: list[MoviePublic]
