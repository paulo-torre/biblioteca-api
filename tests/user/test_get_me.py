from tests.helpers import cleanup_user, make_headers, register_and_verify


def test_get_me_success(client):
    token = register_and_verify(client, "get_me@gmail.com", "getme1", "Senha123!")
    response = client.get("/api/user/me", headers=make_headers(token))
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "email" in data
    assert "username" in data

    assert "stats" in data
    assert "total_saved" in data["stats"]
    assert "total_reviews" in data["stats"]
    assert "total_opinions" in data["stats"]
    assert isinstance(data["stats"]["total_saved"], int)

    assert "member_since" in data

    assert "password" not in data

    cleanup_user("get_me@gmail.com")