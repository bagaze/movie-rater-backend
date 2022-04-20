import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_422_UNPROCESSABLE_ENTITY
)

from app.crud.users import UserCrud
from app.schemas.user import UserCreate
from app.schemas.rating import RatingCreatePublic, RatingPublic, RatingResult

from tests.api.core import get_token


class TestRatingsAPIRoutes:

    def test_routes_exists(self, app: FastAPI, client: TestClient) -> None:
        res = client.post(app.url_path_for("ratings:post-rating"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.get(app.url_path_for("ratings:get-ratings"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.delete(app.url_path_for("ratings:delete-rating-id", rating_id=1), json={})
        assert res.status_code != HTTP_404_NOT_FOUND


@pytest.fixture
def user_test_rating():
    return UserCreate(
        email='rating_user@mail.com',
        username='rating_user',
        password='password'
    )


@pytest.fixture
def test_rating():
    return RatingCreatePublic(
        movie_id=1,
        grade=10
    )


@pytest.fixture
def test_rating_to_update():
    return RatingCreatePublic(
        movie_id=2,
        grade=9
    )


@pytest.fixture
def test_rating_to_get():
    return RatingCreatePublic(
        movie_id=3,
        grade=8
    )


class TestRatingsAPI:

    def test_list_ratings_empty(
        self,
        app: FastAPI,
        client: TestClient
    ):
        res = client.get(app.url_path_for("ratings:get-ratings"))
        assert res.status_code == HTTP_200_OK

        rating_list = RatingResult(**res.json())
        assert rating_list.page == 1
        assert rating_list.results == []
        assert rating_list.total_pages == 0
        assert rating_list.total_results == 0

    async def test_create_rating(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_rating: UserCreate,
        test_rating: RatingCreatePublic
    ):
        new_user = await user_crud.create_new_user(new_user=user_test_rating, is_superuser=False)

        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.post(
            app.url_path_for("ratings:post-rating"),
            headers=headers,
            json=test_rating.dict()
        )
        assert res.status_code == HTTP_201_CREATED

        created_rating = RatingPublic(**res.json())
        assert created_rating.id is not None
        assert created_rating.created_at is not None
        assert created_rating.updated_at is not None
        assert created_rating.user_id == new_user.id
        assert created_rating.grade == test_rating.grade
        assert created_rating.movie_id == test_rating.movie_id

    async def test_create_rating_twice(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
        test_rating: RatingCreatePublic
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.post(
            app.url_path_for("ratings:post-rating"),
            headers=headers,
            json=test_rating.dict()
        )
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_rating(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
        test_rating_to_update: RatingCreatePublic
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.post(
            app.url_path_for("ratings:post-rating"),
            headers=headers,
            json=test_rating_to_update.dict()
        )
        assert res.status_code == HTTP_201_CREATED
        created_rating = RatingPublic(**res.json())

        new_grade = 8
        res = client.put(
            app.url_path_for("ratings:put-rating-id", rating_id=created_rating.id),
            headers=headers,
            json=test_rating_to_update.copy(update={'grade': new_grade}).dict()
        )
        assert res.status_code == HTTP_200_OK
        updated_rating = RatingPublic(**res.json())
        assert updated_rating.id == created_rating.id
        assert updated_rating.movie_id == created_rating.movie_id
        assert updated_rating.user_id == created_rating.user_id
        assert updated_rating.grade == new_grade

    def test_update_rating_does_not_exist(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
        test_rating_to_update: RatingCreatePublic
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.put(
            app.url_path_for("ratings:put-rating-id", rating_id=1000000),
            headers=headers,
            json=test_rating_to_update.dict()
        )
        assert res.status_code == HTTP_404_NOT_FOUND

    def test_get_rating(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
        test_rating_to_get: RatingCreatePublic
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.post(
            app.url_path_for("ratings:post-rating"),
            headers=headers,
            json=test_rating_to_get.dict()
        )
        assert res.status_code == HTTP_201_CREATED
        created_rating = RatingPublic(**res.json())

        res = client.get(
            app.url_path_for("ratings:get-rating-id", rating_id=created_rating.id),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK

        retrieved_rating = RatingPublic(**res.json())
        assert created_rating.id == retrieved_rating.id
        assert retrieved_rating.movie_id == created_rating.movie_id
        assert retrieved_rating.user_id == created_rating.user_id
        assert retrieved_rating.grade == created_rating.grade

    def test_get_rating_does_not_exist(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("ratings:get-rating-id", rating_id=10000),
            headers=headers
        )
        assert res.status_code == HTTP_404_NOT_FOUND

    def test_get_ratings(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("ratings:get-ratings"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK
        ratings = RatingResult(**res.json())
        assert ratings.page == 1
        assert ratings.total_results == 3
        assert ratings.total_pages == 1
        assert ratings.results

    def test_get_ratings_page2(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate,
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("ratings:get-ratings"),
            headers=headers,
            params={
                'page': 2
            }
        )
        assert res.status_code == HTTP_200_OK
        ratings = RatingResult(**res.json())
        assert ratings.page == 2
        assert ratings.total_results == 3
        assert ratings.total_pages == 1
        assert ratings.results == []

    def test_delete_rating(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_rating: UserCreate
    ):
        token = get_token(app, client, user=user_test_rating)
        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }

        res = client.delete(
            app.url_path_for("ratings:delete-rating-id", rating_id=1),
            headers=headers
        )
        assert res.status_code == HTTP_204_NO_CONTENT
        assert res.text == ''

        res = client.delete(
            app.url_path_for("ratings:delete-rating-id", rating_id=10000),
            headers=headers
        )
        assert res.status_code == HTTP_204_NO_CONTENT
        assert res.text == ''

        res = client.get(
            app.url_path_for("ratings:get-ratings"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK
        ratings = RatingResult(**res.json())
        assert ratings.page == 1
        assert ratings.total_results == 2
        assert ratings.total_pages == 1
        assert ratings.results
