from databases import Database
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED
)

from app.crud.users import UserCrud
from app.schemas.user import UserCreate, UserInDB, UserPublic
from app.schemas.token import AccessToken


@pytest.fixture
def user_crud(db: Database) -> UserCrud:
    return UserCrud(db)


class TestUsersAPIRoutes:

    def test_routes_exists(self, app: FastAPI, client: TestClient) -> None:
        res = client.post(app.url_path_for("users:post-user"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.get(app.url_path_for("users:get-users"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

        res = client.get(app.url_path_for("users:get-user-me"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND


class TestUsersAPICreation:

    async def _compare_users(
        self,
        *,
        created_user: UserPublic,
        new_user: UserCreate,
        user_crud: UserCrud
    ):
        assert created_user.username == new_user.username
        assert created_user.email == new_user.email

        user_in_db: UserInDB = await user_crud.get_user_by_username(username=created_user.username)
        assert user_crud.auth_service.verify_password(
            password=new_user.password,
            salt=user_in_db.salt,
            hashed_pw=user_in_db.password
        )
        assert user_in_db.is_active
        assert user_in_db.is_superuser is False
        assert user_in_db.created_at is not None
        assert user_in_db.updated_at is not None

    async def test_create_user(self, app: FastAPI, client: TestClient, user_crud: UserCrud) -> None:
        new_user = UserCreate(
            email='john.doe@mail.com',
            username='john_doe',
            password='password'
        )
        res = client.post(app.url_path_for("users:post-user"), json=new_user.dict())
        assert res.status_code == HTTP_201_CREATED

        created_user = UserPublic(**res.json())
        await self._compare_users(
            created_user=created_user,
            new_user=new_user,
            user_crud=user_crud
        )

    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
            ("email", "john.doe@mail.com", 400),
            ("username", "john_doe", 400),
            ("email", "invalid_email@one@two.io", 422),
            ("password", "mini", 422),
            ("username", "john_doe@#$%^<>", 422),
            ("username", "ab", 422),
        ),
    )
    async def test_user_registration_fails_when_credentials_are_taken(
        self,
        app: FastAPI,
        client: TestClient,
        attr: str,
        value: str,
        status_code: int
    ) -> None:
        new_user = {
            'email': 'not_taken@mail.com',
            'username': 'nottaken',
            'password': 'nottakenpass'
        }
        new_user[attr] = value
        res = client.post(app.url_path_for("users:post-user"), json=new_user)
        assert res.status_code == status_code


@pytest.fixture
def user_test_login():
    return UserCreate(
        email='jane.doe@mail.com',
        username='jane_doe',
        password='password'
    )


class TestUsersAPILogin:

    async def test_user_login(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_login: UserCreate,
        user_crud: UserCrud
    ):
        await user_crud.create_new_user(new_user=user_test_login, is_superuser=False)

        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={'username': user_test_login.email, 'password': user_test_login.password}
        )

        token = AccessToken(**res.json())
        assert token.token_type == 'Bearer'
        assert token.access_token is not None

    def test_user_get_me(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_login: UserCreate
    ):
        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={'username': user_test_login.email, 'password': user_test_login.password}
        )
        assert res.status_code == HTTP_201_CREATED
        token = AccessToken(**res.json())

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-user-me"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK

        user_me = UserPublic(**res.json())
        assert user_test_login.username == user_me.username
        assert user_test_login.email == user_me.email

    def test_token_not_existing_user(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        fake_user = {
            'email': 'fake_user@mail.com',
            'username': 'fake_user',
            'password': 'fake_pass'
        }
        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={'username': fake_user['email'], 'password': fake_user['password']}
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED

    def test_user_access_prevention(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_login: UserCreate
    ):
        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={'username': user_test_login.email, 'password': user_test_login.password}
        )
        assert res.status_code == HTTP_201_CREATED
        token = AccessToken(**res.json())

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-users"),
            headers=headers
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED


@pytest.fixture
def user_test_admin_login():
    return UserCreate(
        email='admin@mail.com',
        username='admin',
        password='password'
    )


class TestUsersAdminAPILogin:

    async def test_admin_login(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_admin_login: UserCreate,
        user_crud: UserCrud
    ):
        await user_crud.create_new_user(new_user=user_test_admin_login, is_superuser=True)

        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={
                'username': user_test_admin_login.email, 'password': user_test_admin_login.password
            }
        )

        token = AccessToken(**res.json())
        assert token.token_type == 'Bearer'
        assert token.access_token is not None

    def test_admin_get_me(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_admin_login: UserCreate
    ):
        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={
                'username': user_test_admin_login.email, 'password': user_test_admin_login.password
            }
        )
        assert res.status_code == HTTP_201_CREATED
        token = AccessToken(**res.json())

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-user-me"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK

        user_me = UserPublic(**res.json())
        assert user_test_admin_login.username == user_me.username
        assert user_test_admin_login.email == user_me.email

    def test_admin_access_restricted_endpoints(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_admin_login: UserCreate
    ):
        res = client.post(
            app.url_path_for("tokens:post-token"),
            data={
                'username': user_test_admin_login.email, 'password': user_test_admin_login.password
            }
        )
        assert res.status_code == HTTP_201_CREATED
        token = AccessToken(**res.json())

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-users"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK
