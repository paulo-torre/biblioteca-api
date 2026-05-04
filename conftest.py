import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user():
    return {
        "email": "teste@gmail.com",
        "username": "testuser123",
        "password": "Senha123!"
    }