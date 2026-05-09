from tests.helpers import register_and_verify, make_headers, cleanup_user
from app.database import supabase

def test_forgot_password_success(client):
    token = register_and_verify(client, "forgot_test@gmail.com", "forgotusertest1", "Senha123!")
    response = client.post("/api/auth/forgot-password", json={"email": "forgot_test@gmail.com"})
    assert response.status_code == 200
    assert "message" in response.json()
    cleanup_user("forgot_test@gmail.com")

def test_forgot_password_nonexistent_email(client):
    response = client.post("/api/auth/forgot-password", json={"email": "noexist_email_teste@gmail.com"})
    assert response.status_code == 404

def test_reset_password_wrong_code(client):
    token = register_and_verify(client, "reset_wrong@gmail.com", "resetwrong1", "Senha123!")
    client.post("/api/auth/forgot-password", json={"email": "reset_wrong@gmail.com"})
    response = client.post("/api/auth/reset-password", json={
        "email": "reset_wrong@gmail.com",
        "code": "000000",
        "new_password": "NovaSenha123!"
    })
    assert response.status_code == 400
    cleanup_user("reset_wrong@gmail.com")

def test_reset_password_same_as_old(client):
    token = register_and_verify(client, "reset_same@gmail.com", "resetsame1", "Senha123!")
    client.post("/api/auth/forgot-password", json={"email": "reset_same@gmail.com"})
    result = supabase.table("users").select("verify_code").eq("email", "reset_same@gmail.com").execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/auth/reset-password", json={
        "email": "reset_same@gmail.com",
        "code": code,
        "new_password": "Senha123!"
    })
    assert response.status_code == 400
    cleanup_user("reset_same@gmail.com")

def test_reset_password_success(client):
    token = register_and_verify(client, "reset_success@gmail.com", "resetsuccess1", "Senha123!")
    client.post("/api/auth/forgot-password", json={"email": "reset_success@gmail.com"})
    result = supabase.table("users").select("verify_code").eq("email", "reset_success@gmail.com").execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/auth/reset-password", json={
        "email": "reset_success@gmail.com",
        "code": code,
        "new_password": "NovaSenha123!"
    })
    assert response.status_code == 200
    assert "message" in response.json()
    cleanup_user("reset_success@gmail.com")