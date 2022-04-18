from pydantic import conint

from app.schemas.core import (
    CoreModel,
    DateTimeModelMixin,
    IDModelMixin,
    ListResult
)


class RatingBase(CoreModel):
    """
    Rating base model
    """
    movie_id: int
    user_id: int
    grade: conint(ge=0, le=10)


class RatingCreatePublic(CoreModel):
    """
    Base minus user_id (determined from the connected user)
    """
    movie_id: int
    grade: conint(ge=0, le=10)


class RatingUpdatePublic(RatingCreatePublic):
    """
    Same as RatingCreatePublic
    """


class RatingCreate(RatingBase):
    """
    Same as RatingBase
    """


class RatingUpdate(RatingCreate):
    """
    Same as RatingCreate
    """


class RatingInDB(IDModelMixin, DateTimeModelMixin, RatingBase):
    """
    Add in id, created_at, updated_at
    """
    pass


class RatingPublic(IDModelMixin, DateTimeModelMixin, RatingBase):
    """
    Same as InDB
    """
    pass


class RatingResult(ListResult):
    results: list[RatingPublic]
