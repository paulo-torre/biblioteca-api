import pytest
from app.database import supabase

@pytest.fixture(autouse=True, scope="module")
def cleanup():
    supabase.table("users").delete().eq("email", "teste@gmail.com").execute()
    supabase.table("users").delete().eq("email", "teste_novo@gmail.com").execute()
    yield
    supabase.table("users").delete().eq("email", "teste@gmail.com").execute()
    supabase.table("users").delete().eq("email", "teste_novo@gmail.com").execute()
    supabase.table("users").delete().eq("email", "unverified_teste@gmail.com").execute()

# ============================================================
# /auth/register
# ============================================================

def test_register_success(client, test_user):
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 200
    assert "message" in response.json()

def test_register_duplicate_email(client, test_user):
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 409

def test_register_duplicate_username(client, test_user):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro@gmail.com"
    })
    assert response.status_code == 409

def test_register_invalid_password_too_short(client, test_user):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro2@gmail.com",
        "password": "Ab1!"
    })
    assert response.status_code == 422

def test_register_invalid_password_no_special(client, test_user):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro3@gmail.com",
        "password": "Senha1234"
    })
    assert response.status_code == 422

def test_register_invalid_email(client, test_user):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "nao-eh-um-email"
    })
    assert response.status_code == 422

# ============================================================
# /auth/verify-email
# ============================================================

def test_verify_email_wrong_code(client, test_user):
    response = client.post("/api/auth/verify-email", json={
        "email": test_user["email"],
        "code": "000000"
    })
    assert response.status_code == 400

def test_verify_email_success(client, test_user):
    result = supabase.table("users").select("verify_code").eq("email", test_user["email"]).execute()
    code = result.data[0]["verify_code"]

    response = client.post("/api/auth/verify-email", json={
        "email": test_user["email"],
        "code": code
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# ============================================================
# /auth/login
# ============================================================

def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "SenhaErrada1!"
    })
    assert response.status_code == 401

def test_login_wrong_email(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "naoexiste@gmail.com",
        "password": test_user["password"]
    })
    assert response.status_code == 401

def test_login_unverified_email(client):
    unverified = {
        "email": "unverified_teste@gmail.com",
        "username": "unverified123",
        "password": "Senha123!"
    }
    client.post("/api/auth/register", json=unverified)
    response = client.post("/api/auth/login", json={
        "email": unverified["email"],
        "password": unverified["password"]
    })
    assert response.status_code == 403

# ============================================================
# HELPERS
# ============================================================

def register_and_verify(client, email, username, password):
    """Registra e verifica um usuário, retornando o token."""
    client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": password
    })
    result = supabase.table("users").select("verify_code").eq("email", email).execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/auth/verify-email", json={"email": email, "code": code})
    return response.json()["access_token"]

def make_headers(token):
    return {"Authorization": f"Bearer {token}"}

def cleanup_user(email):
    supabase.table("users").delete().eq("email", email).execute()

# ============================================================
# /api/user/me/username
# ============================================================

def test_change_username_success(client):
    token = register_and_verify(client, "u_username@gmail.com", "usernametest1", "Senha123!")
    response = client.put("/api/user/me/username",
        json={"username": "usernametest2"},
        headers=make_headers(token)
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    cleanup_user("u_username@gmail.com")

def test_change_username_duplicate(client):
    token = register_and_verify(client, "u_dupuser@gmail.com", "dupusertest1", "Senha123!")
    response = client.put("/api/user/me/username",
        json={"username": "dupusertest1"},
        headers=make_headers(token)
    )
    assert response.status_code == 409
    cleanup_user("u_dupuser@gmail.com")

def test_change_username_too_short(client):
    token = register_and_verify(client, "u_short@gmail.com", "shorttest1", "Senha123!")
    response = client.put("/api/user/me/username",
        json={"username": "ab"},
        headers=make_headers(token)
    )
    assert response.status_code == 422
    cleanup_user("u_short@gmail.com")

def test_change_username_unauthorized(client):
    response = client.put("/api/user/me/username", json={"username": "qualquer123"})
    assert response.status_code == 401


# ============================================================
# /api/user/me/password
# ============================================================

def test_change_password_success(client):
    token = register_and_verify(client, "u_pass@gmail.com", "passtest1", "Senha123!")
    response = client.put("/api/user/me/password", json={
        "password": "Senha123!",
        "new_password": "NovaSenha123!"
    }, headers=make_headers(token))
    assert response.status_code == 200
    cleanup_user("u_pass@gmail.com")

def test_change_password_wrong_current(client):
    token = register_and_verify(client, "u_wrongpass@gmail.com", "wrongpass1", "Senha123!")
    response = client.put("/api/user/me/password", json={
        "password": "SenhaErrada1!",
        "new_password": "NovaSenha123!"
    }, headers=make_headers(token))
    assert response.status_code == 401
    cleanup_user("u_wrongpass@gmail.com")

def test_change_password_invalid_new(client):
    token = register_and_verify(client, "u_invalidpass@gmail.com", "invalidpass1", "Senha123!")
    response = client.put("/api/user/me/password", json={
        "password": "Senha123!",
        "new_password": "fraca"
    }, headers=make_headers(token))
    assert response.status_code == 422
    cleanup_user("u_invalidpass@gmail.com")

def test_change_password_unauthorized(client):
    response = client.put("/api/user/me/password", json={
        "password": "Senha123!",
        "new_password": "NovaSenha123!"
    })
    assert response.status_code == 401


# ============================================================
# /api/user/me/email  +  /api/user/me/verify-email-change
# ============================================================

def test_request_email_change_success(client):
    token = register_and_verify(client, "u_email@gmail.com", "emailtest1", "Senha123!")
    response = client.put("/api/user/me/email",
        json={"new_email": "u_email_novo@gmail.com"},
        headers=make_headers(token)
    )
    assert response.status_code == 200
    assert "message" in response.json()
    cleanup_user("u_email@gmail.com")

def test_request_email_change_duplicate(client):
    token = register_and_verify(client, "u_dupemail@gmail.com", "dupemailtest1", "Senha123!")
    response = client.put("/api/user/me/email",
        json={"new_email": "u_dupemail@gmail.com"},
        headers=make_headers(token)
    )
    assert response.status_code == 409
    cleanup_user("u_dupemail@gmail.com")

def test_request_email_change_unauthorized(client):
    response = client.put("/api/user/me/email", json={"new_email": "x@gmail.com"})
    assert response.status_code == 401

def test_verify_email_change_wrong_code(client):
    token = register_and_verify(client, "u_wrongcode@gmail.com", "wrongcodetest1", "Senha123!")
    client.put("/api/user/me/email",
        json={"new_email": "u_wrongcode_novo@gmail.com"},
        headers=make_headers(token)
    )
    response = client.post("/api/user/me/verify-email-change",
        json={"code": "000000"},
        headers=make_headers(token)
    )
    assert response.status_code == 400
    cleanup_user("u_wrongcode@gmail.com")

def test_verify_email_change_success(client):
    token = register_and_verify(client, "u_emailchange@gmail.com", "emailchange1", "Senha123!")
    client.put("/api/user/me/email",
        json={"new_email": "u_emailchange_novo@gmail.com"},
        headers=make_headers(token)
    )
    result = supabase.table("users").select("verify_code").eq("email", "u_emailchange@gmail.com").execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/user/me/verify-email-change",
        json={"code": code},
        headers=make_headers(token)
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    cleanup_user("u_emailchange_novo@gmail.com")


# ============================================================
# /api/user/me/request-delete  +  DELETE /api/user/me
# ============================================================

def test_request_delete_success(client):
    token = register_and_verify(client, "u_delete@gmail.com", "deletetest1", "Senha123!")
    response = client.post("/api/user/me/request-delete", headers=make_headers(token))
    assert response.status_code == 200
    assert "message" in response.json()
    cleanup_user("u_delete@gmail.com")

def test_request_delete_unauthorized(client):
    response = client.post("/api/user/me/request-delete")
    assert response.status_code == 401

def test_delete_account_wrong_code(client):
    token = register_and_verify(client, "u_deletewrong@gmail.com", "deletewrong1", "Senha123!")
    client.post("/api/user/me/request-delete", headers=make_headers(token))
    response = client.request("DELETE", "/api/user/me",
        json={"code": "000000"},
        headers=make_headers(token)
    )
    assert response.status_code == 400
    cleanup_user("u_deletewrong@gmail.com")

def test_delete_account_success(client):
    token = register_and_verify(client, "u_deletesuccess@gmail.com", "deletesuccess1", "Senha123!")
    client.post("/api/user/me/request-delete", headers=make_headers(token))
    result = supabase.table("users").select("verify_code").eq("email", "u_deletesuccess@gmail.com").execute()
    code = result.data[0]["verify_code"]
    response = client.request("DELETE", "/api/user/me",
        json={"code": code},
        headers=make_headers(token)
    )
    assert response.status_code == 204