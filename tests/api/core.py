from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.status import HTTP_201_CREATED

from app.schemas import token, user


# Retrive a token for a user
def get_token(app_: FastAPI, client_: TestClient, *, user: user.UserCreate) -> token.AccessToken:
    res = client_.post(
        app_.url_path_for("tokens:post-token"),
        data={'username': user.email, 'password': user.password}
    )
    assert res.status_code == HTTP_201_CREATED

    return token.AccessToken(**res.json())
