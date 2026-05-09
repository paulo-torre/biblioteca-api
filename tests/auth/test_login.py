def test_login_success(client, verified_user):
    response = client.post("/api/auth/login", json={
        "email": verified_user["email"],
        "password": verified_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, verified_user):
    response = client.post("/api/auth/login", json={
        "email": verified_user["email"],
        "password": "SenhaErrada1!"
    })
    assert response.status_code == 401

def test_login_wrong_email(client, verified_user):
    response = client.post("/api/auth/login", json={
        "email": "naoexiste@gmail.com",
        "password": verified_user["password"]
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