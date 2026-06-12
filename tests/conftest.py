import pytest
import bcrypt
import random
import string
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.services.database import supabase
from . import helpers

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def cleanup():
    supabase.table("users").delete().eq("email", "teste@gmail.com").execute()
    supabase.table("users").delete().eq("email", "teste_novo@gmail.com").execute()
    supabase.table("users").delete().eq("email", "unverified_teste@gmail.com").execute()
    yield
    supabase.table("users").delete().eq("email", "teste@gmail.com").execute()
    supabase.table("users").delete().eq("email", "teste_novo@gmail.com").execute()
    supabase.table("users").delete().eq("email", "unverified_teste@gmail.com").execute()

@pytest.fixture(scope="module")
def test_user():
    return {
        "email": "teste@gmail.com",
        "username": "testuser123",
        "password": "Senha123!"
    }


@pytest.fixture(autouse=True)
def ensure_helpers_cleanup():
    # make sure helpers._to_cleanup is reset for each test
    helpers._to_cleanup = []
    yield
    # always attempt to cleanup any registered emails, even if the test failed
    for email in list(helpers._to_cleanup):
        supabase.table("users").delete().eq("email", email).execute()
    helpers._to_cleanup = []

@pytest.fixture(scope="module")
def verified_user(client):
    email = "verified_test@gmail.com"
    username = "verifiedtest1"
    password = "Senha123!"

    # limpa antes
    supabase.table("users").delete().eq("email", email).execute()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    supabase.table("users").insert({
        "email": email,
        "username": username,
        "password": hashed,
        "email_verified": True,
    }).execute()

    yield {"email": email, "username": username, "password": password}

    # limpa depois
    supabase.table("users").delete().eq("email", email).execute()

@pytest.fixture(scope="module")
def unverified_user(client):
    email = "unverified_test@gmail.com"
    username = "unverifiedtest1"
    password = "Senha123!"

    # limpa antes
    supabase.table("users").delete().eq("email", email).execute()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    supabase.table("users").insert({
        "email": email,
        "username": username,
        "password": hashed,
        "email_verified": False,
        "verify_code": code,
        "verify_code_expires": expires_at.isoformat()
    }).execute()

    yield {"email": email, "username": username, "password": password}

    # limpa depois
    supabase.table("users").delete().eq("email", email).execute()


@pytest.fixture
def book_user_factory():
    created_users = []

    def _create(email, username, password="Senha123!"):
        user = helpers.create_verified_user(email, username, password)
        created_users.append(user)
        return user

    yield _create

    for user in created_users:
        helpers.cleanup_book_data(user["user_id"])
        helpers.cleanup_user(user["email"])


@pytest.fixture
def mock_book_exists(monkeypatch):
    helpers.mock_validate_book_exists(monkeypatch)
