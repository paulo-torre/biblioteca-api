from tests.helpers import save_book, delete_saved_book, make_headers


def test_save_book_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("save_user@gmail.com", "saveuser1")
    resp = save_book(client, user["token"], "OL1234M")
    assert resp.status_code == 200


def test_save_book_unauthorized(client):
    resp = client.post("/api/books/saved", json={"book_id": "OL1234M"})
    assert resp.status_code == 401


def test_save_book_invalid_data(client, book_user_factory):
    user = book_user_factory("save_inv@gmail.com", "saveinv1")
    resp = save_book(client, user["token"], "INVALID")
    assert resp.status_code == 422


def test_save_book_duplicate(client, book_user_factory, mock_book_exists):
    user = book_user_factory("save_dup@gmail.com", "savedup1")
    first = save_book(client, user["token"], "OL5678M")
    assert first.status_code == 200
    second = save_book(client, user["token"], "OL5678M")
    assert second.status_code == 409


def test_get_saved_books(client, book_user_factory, mock_book_exists):
    user = book_user_factory("save_list@gmail.com", "savelist1")
    save_book(client, user["token"], "OL9999M")
    resp = client.get("/api/books/saved", headers=make_headers(user["token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data


def test_delete_saved_book_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("save_del@gmail.com", "savedel1")
    save_book(client, user["token"], "OL2222M")
    resp = delete_saved_book(client, user["token"], "OL2222M")
    assert resp.status_code == 200


def test_delete_saved_book_not_found(client, book_user_factory):
    user = book_user_factory("save_notfound@gmail.com", "savenf1")
    resp = delete_saved_book(client, user["token"], "OL0000M")
    assert resp.status_code == 404


def test_delete_saved_unauthorized(client):
    resp = client.request("DELETE", "/api/books/saved/OL1111M", json={"book_id": "OL1111M"})
    assert resp.status_code == 401
