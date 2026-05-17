def test_register_success(client, test_user, cleanup):
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 200
    assert "message" in response.json()

def test_register_duplicate_email(client, test_user, cleanup):
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 409

def test_register_duplicate_username(client, test_user, cleanup):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro@gmail.com"
    })
    assert response.status_code == 409

def test_register_invalid_password_too_short(client, test_user, cleanup):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro2@gmail.com",
        "password": "Ab1!"
    })
    assert response.status_code == 422

def test_register_invalid_password_no_special(client, test_user, cleanup):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "outro3@gmail.com",
        "password": "Senha1234"
    })
    assert response.status_code == 422

def test_register_invalid_email(client, test_user, cleanup):
    response = client.post("/api/auth/register", json={
        **test_user,
        "email": "nao-eh-um-email"
    })
    assert response.status_code == 422
