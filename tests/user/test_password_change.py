from tests.helpers import register_and_verify, make_headers, cleanup_user

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