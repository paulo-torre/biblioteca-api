from tests.helpers import register_and_verify, make_headers, cleanup_user

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