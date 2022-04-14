from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED

from app.schemas.user import UserCreate


@pytest.fixture
def new_user():
    return UserCreate(
        email='john.doe@mail.com',
        username='john_doe',
        password='password'
    )


@pytest.fixture
def new_user_2():
    return UserCreate(
        email='john.doe2@mail.com',
        username='john_doe2',
        password='password2'
    )


class TestUsers:

    def test_routes_exists(self, app: FastAPI, client: TestClient) -> None:
        res = client.post(app.url_path_for("users:post-user"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.get(app.url_path_for("users:get-users"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.get(app.url_path_for("users:get-user-me"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    def test_create_user(
        self,
        app: FastAPI,
        client: TestClient,
        new_user: UserCreate,
        new_user_2: UserCreate
    ) -> None:
        res = client.post(app.url_path_for("users:post-user"), json=new_user.dict())
        res = client.post(app.url_path_for("users:post-user"), json=new_user_2.dict())
        assert res.status_code == HTTP_201_CREATED

        # created_user = UserCreate(**res.json())
        # assert created_user == new_user
