from tests.helpers import register_and_verify, make_headers, cleanup_user
from app.services.database import supabase

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