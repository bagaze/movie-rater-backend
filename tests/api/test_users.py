from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED
)

from app.crud.users import UserCrud
from app.schemas.user import UserCreate, UserInDB, UserPublic
from app.schemas.token import AccessToken


def get_token(app_: FastAPI, client_: TestClient, *, user: UserCreate) -> AccessToken:
    res = client_.post(
        app_.url_path_for("tokens:post-token"),
        data={'username': user.email, 'password': user.password}
    )
    assert res.status_code == HTTP_201_CREATED

    return AccessToken(**res.json())


async def get_or_create_user(
    user_crud_: UserCrud, *, user_c: UserCreate, is_superuser: bool = False
) -> UserPublic:
    user = await user_crud_.get_user_by_email(email=user_c.email)

    if user is None:
        new_user = UserCreate(
            email=user_c.email, username=user_c.username, password=user_c.password
        )
        user = await user_crud_.create_new_user(
            new_user=new_user, is_superuser=is_superuser
        )
        assert user.id is not None

    assert user.id is not None
    return user


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


@pytest.fixture
def user_test_api_retrieval():
    return UserCreate(
        email='test_api_retrieval@mail.com',
        username='test_api_retrieval',
        password='password'
    )


class TestUsersAPIRetrieval:

    async def test_user_get_by_id(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_api_retrieval: UserCreate,
        user_crud: UserCrud
    ):
        new_user: UserInDB = await user_crud.create_new_user(
            new_user=user_test_api_retrieval, is_superuser=False
        )

        res = client.get(
            app.url_path_for("users:get-user-id", user_id=new_user.id)
        )
        assert res.status_code == HTTP_200_OK

        retrieved_user = UserPublic(**res.json())
        assert retrieved_user.id
        assert retrieved_user.email == new_user.email
        assert retrieved_user.username == new_user.username

    def test_user_get_by_id_not_existing(
        self,
        app: FastAPI,
        client: TestClient
    ):
        not_existing_id = 1000000
        res = client.get(
            app.url_path_for("users:get-user-id", user_id=not_existing_id)
        )
        assert res.status_code == HTTP_404_NOT_FOUND


class TestUsersAPILogin:

    async def test_user_login(
        self,
        app: FastAPI,
        client: TestClient,
        user_test_login: UserCreate,
        user_crud: UserCrud
    ):
        created_user = await user_crud.create_new_user(new_user=user_test_login, is_superuser=False)
        assert created_user is not None

        get_token(app, client, user=user_test_login)

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


@pytest.fixture
def admin_test_login():
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
        admin_test_login: UserCreate,
        user_crud: UserCrud
    ):
        await user_crud.create_new_user(new_user=admin_test_login, is_superuser=True)

        get_token(
            app,
            client,
            user=admin_test_login
        )

    def test_admin_get_me(
        self,
        app: FastAPI,
        client: TestClient,
        admin_test_login: UserCreate
    ):
        token = get_token(
            app,
            client,
            user=admin_test_login
        )

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-user-me"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK

        user_me = UserPublic(**res.json())
        assert admin_test_login.username == user_me.username
        assert admin_test_login.email == user_me.email

    def test_admin_access_restricted_endpoints(
        self,
        app: FastAPI,
        client: TestClient,
        admin_test_login: UserCreate
    ):
        token = get_token(
            app,
            client,
            user=admin_test_login
        )

        headers = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        res = client.get(
            app.url_path_for("users:get-users"),
            headers=headers
        )
        assert res.status_code == HTTP_200_OK


@pytest.fixture
def user_test_modify():
    return UserCreate(
        email='henry.doe@mail.com',
        username='henry_doe',
        password='password'
    )


@pytest.fixture
def user_two_test_modify():
    return UserCreate(
        email='jack.doe@mail.com',
        username='jack_doe',
        password='password'
    )


@pytest.fixture
def admin_test_modify():
    return UserCreate(
        email='admin_mod@mail.com',
        username='admin_mod',
        password='password'
    )


class TestUsersAPIModify:

    async def test_modify_user_without_token(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_modify: UserCreate
    ):
        user_1 = await get_or_create_user(
            user_crud, user_c=user_test_modify, is_superuser=False
        )
        res = client.put(
            app.url_path_for("users:put-user-id", user_id=user_1.id),
            data={
                'username': 'mod_username', 'email': 'mod_email@mail.com'
            }
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED

    async def test_modify_user(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_modify: UserCreate
    ):
        user_1 = await get_or_create_user(
            user_crud, user_c=user_test_modify, is_superuser=False
        )
        token_user_1 = get_token(app, client, user=user_test_modify)

        headers = {
            'Authorization': f'{token_user_1.token_type} {token_user_1.access_token}'
        }
        res = client.put(
            app.url_path_for("users:put-user-id", user_id=user_1.id),
            headers=headers,
            json={
                'username': 'mod_username', 'email': 'mod_email@mail.com'
            }
        )
        assert res.status_code == HTTP_200_OK
        user_mod_1 = UserPublic(**res.json())
        assert user_mod_1.username == 'mod_username'
        assert user_mod_1.email == 'mod_email@mail.com'
        assert user_mod_1.id == user_1.id

    async def test_modify_another_user(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_modify: UserCreate,
        user_two_test_modify: UserCreate
    ):
        await get_or_create_user(
            user_crud, user_c=user_test_modify, is_superuser=False
        )
        user_2 = await get_or_create_user(
            user_crud, user_c=user_two_test_modify, is_superuser=False
        )
        token_user_1 = get_token(app, client, user=user_test_modify)

        headers = {
            'Authorization': f'{token_user_1.token_type} {token_user_1.access_token}'
        }
        res = client.put(
            app.url_path_for("users:put-user-id", user_id=user_2.id),
            headers=headers,
            json={
                'username': 'mod_username', 'email': 'mod_email@mail.com'
            }
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED

    async def test_modify_users_as_admin(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_modify: UserCreate,
        admin_test_modify: UserCreate
    ):
        await get_or_create_user(
            user_crud, user_c=admin_test_modify, is_superuser=True
        )
        user_1 = await get_or_create_user(
            user_crud, user_c=user_test_modify, is_superuser=False
        )
        token_admin = get_token(app, client, user=admin_test_modify)

        headers = {
            'Authorization': f'{token_admin.token_type} {token_admin.access_token}'
        }
        res = client.put(
            app.url_path_for("users:put-user-id", user_id=user_1.id),
            headers=headers,
            json={
                'username': 'username_mod_by_admin', 'email': 'email_mod_by_admin@mail.com'
            }
        )
        assert res.status_code == HTTP_200_OK

        user_mod_1 = UserPublic(**res.json())
        assert user_mod_1.username == 'username_mod_by_admin'
        assert user_mod_1.email == 'email_mod_by_admin@mail.com'


@pytest.fixture
def user_test_delete():
    return UserCreate(
        email='robert.doe@mail.com',
        username='robert_doe',
        password='password'
    )


@pytest.fixture
def admin_test_delete():
    return UserCreate(
        email='admin_del@mail.com',
        username='admin_del',
        password='password'
    )


class TestDeleteUser:

    async def test_delete_admin(
        self,
        app: FastAPI,
        client: TestClient,
        user_crud: UserCrud,
        user_test_delete: UserCreate,
        admin_test_delete: UserCreate
    ):
        user = await get_or_create_user(user_crud, user_c=user_test_delete)
        admin = await get_or_create_user(user_crud, user_c=admin_test_delete, is_superuser=True)

        admin_token = get_token(app, client, user=admin_test_delete)
        headers = {
            'Authorization': f'{admin_token.token_type} {admin_token.access_token}'
        }

        res = client.delete(
            app.url_path_for("users:delete-user-id", user_id=user.id),
            headers=headers
        )
        assert res.status_code == HTTP_204_NO_CONTENT

        res = client.get(
            app.url_path_for("users:get-user-id", user_id=user.id),
            headers=headers
        )
        assert res.status_code == HTTP_404_NOT_FOUND

        res = client.delete(
            app.url_path_for("users:delete-user-id", user_id=admin.id),
            headers=headers
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED
