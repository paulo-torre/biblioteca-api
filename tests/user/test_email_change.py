from tests.helpers import register_and_verify, make_headers, cleanup_user
from app.database import supabase

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