import os
from typing import Generator
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from databases import Database
import logging

import alembic
from alembic.config import Config

logger = logging.getLogger()


# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


# Create a new application for testing
@pytest.fixture
def app() -> FastAPI:
    from app.app import get_application
    return get_application()


# Grab a reference to our database when needed
@pytest.fixture(scope="module")
def db_session() -> Database:
    from app.db.deps import db_session
    return db_session


# Make requests in our tests
@pytest.fixture
def client(app: FastAPI) -> Generator:
    with TestClient(app) as c:
        yield c
