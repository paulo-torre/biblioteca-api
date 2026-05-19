from tests.helpers import create_opinion, delete_opinion, make_headers, update_opinion


def test_create_opinion_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_user@gmail.com", "opuser1")
    resp = create_opinion(client, user["token"], "OL1234M", "liked")
    assert resp.status_code == 200


def test_create_opinion_unauthorized(client):
    resp = client.post("/api/books/opinions", json={"book_id": "OL1234M", "opinion": "liked"})
    assert resp.status_code == 401


def test_create_opinion_invalid_data(client, book_user_factory):
    user = book_user_factory("op_inv@gmail.com", "opinv1")
    resp = create_opinion(client, user["token"], "INVALID", "bad")
    assert resp.status_code in (422, 400)


def test_create_opinion_duplicate(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_dup@gmail.com", "opdup1")
    first = create_opinion(client, user["token"], "OL7777M", "loved")
    assert first.status_code == 200
    second = create_opinion(client, user["token"], "OL7777M", "loved")
    assert second.status_code == 409


def test_edit_opinion_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_edit@gmail.com", "opedit1")
    create_opinion(client, user["token"], "OL3333M", "liked")
    resp = update_opinion(client, user["token"], "OL3333M", "loved")
    assert resp.status_code == 200


def test_edit_opinion_not_found(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_nf@gmail.com", "opnf1")
    resp = update_opinion(client, user["token"], "OL4444M", "loved")
    assert resp.status_code == 404


def test_edit_opinion_unauthorized(client):
    resp = client.put("/api/books/opinions", json={"book_id": "OL1234M", "opinion": "loved"})
    assert resp.status_code == 401


def test_delete_opinion_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_del@gmail.com", "opdel1")
    create_opinion(client, user["token"], "OL5555M", "disliked")
    resp = delete_opinion(client, user["token"], "OL5555M")
    assert resp.status_code == 200


def test_delete_opinion_not_found(client, book_user_factory):
    user = book_user_factory("op_del_nf@gmail.com", "opdelnf1")
    resp = delete_opinion(client, user["token"], "OL6666M")
    assert resp.status_code == 404


def test_get_opinions_list(client, book_user_factory, mock_book_exists):
    user = book_user_factory("op_list@gmail.com", "oplist1")
    create_opinion(client, user["token"], "OL8888M", "liked")
    resp = client.get("/api/books/opinions", headers=make_headers(user["token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data


def test_get_book_opinions_pagination(client, book_user_factory, mock_book_exists):
    user = book_user_factory("opinion_pag1@gmail.com","opinion_pag1")
    for i in range(4):
        create_opinion(client, user["token"], f"OL808{i}M", "loved")

    resp = client.get(
        "/api/books/opinions?page=1&limit=2", headers=make_headers(user["token"])
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 2


def test_get_book_opinions_pagination_invalid_limit(client, book_user_factory, mock_book_exists):
    user = book_user_factory(
        "opinions_invalid_lmt@gmail.com", "opinions_invalid_lmt1"
    )
    create_opinion(client, user["token"], "OL8080M", "disliked")
    resp = client.get(
        "/api/books/opinions?limit=999", headers=make_headers(user["token"])
    )
    assert resp.status_code == 422


def test_get_book_opinions_pagination_invalid_page(client, book_user_factory, mock_book_exists):
    user = book_user_factory(
        "opinions_invalidpage@gmail.com", "opinions_invalidpage1"
    )
    create_opinion(client, user["token"], "OL8080M", "liked")
    resp = client.get("/api/books/opinions?page=0", headers=make_headers(user["token"]))
    assert resp.status_code == 422
