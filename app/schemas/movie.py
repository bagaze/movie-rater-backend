from datetime import date, datetime
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
        regex='^tt[0-9]{7,8}',  # noqa: F722
        min_length=9,
        max_length=10
    )
    directors: list[str] | None
    avg_rating: confloat(ge=0.0, le=10.0) | None
    theatrical_release_date: datetime | None

    @root_validator(pre=True)
    def get_directors(cls, values: dict) -> dict:
        directors = (crew_member['name']
            for crew_member in values['credits']['crew']
                if crew_member['job'] == 'Director')

        return {**values, 'directors': list(directors)}

    @root_validator(pre=True)
    def get_theatrical_release_date(cls, values: dict) -> datetime | None:
        theatrical_release_date = None

        fr_release_dates = next((release_dates
            for release_dates in values['release_dates']['results']
                if release_dates['iso_3166_1'] == 'FR'), None)

        if fr_release_dates is not None:
            theatrical_release_date = next((release_date['release_date']
                for release_date in fr_release_dates['release_dates']
                    if release_date['type'] == 3), None)

        return {**values, 'theatrical_release_date': theatrical_release_date}

    class Config:
        extra: Extra.allow


class MovieResult(ListResult):
    results: list[MoviePublic]
