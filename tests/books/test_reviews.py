from tests.helpers import create_review, update_review, delete_review, make_headers


def test_create_review_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_user@gmail.com", "revuser1")
    resp = create_review(client, user["token"], "OL1010M", 4.5, "Bom livro")
    assert resp.status_code == 200


def test_create_review_duplicate(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_dup@gmail.com", "revdup1")
    first = create_review(client, user["token"], "OL2020M", 3.0, "Ok")
    assert first.status_code == 200
    second = create_review(client, user["token"], "OL2020M", 3.0, "Ok")
    assert second.status_code == 409


def test_create_review_invalid_rating(client, book_user_factory):
    user = book_user_factory("rev_inv@gmail.com", "revinv1")
    resp = create_review(client, user["token"], "OL3030M", 6.0, "Nota inválida")
    assert resp.status_code == 422


def test_create_review_unauthorized(client):
    resp = client.post("/api/books/reviews", json={"book_id": "OL1234M", "rating": 4.0})
    assert resp.status_code == 401


def test_edit_review_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_edit@gmail.com", "revedit1")
    create_review(client, user["token"], "OL4040M", 2.5, "Primeira")
    resp = update_review(client, user["token"], "OL4040M", 4.0, "Atualizada")
    assert resp.status_code == 200


def test_edit_review_not_found(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_nf@gmail.com", "revnf1")
    resp = update_review(client, user["token"], "OL5050M", 4.0, "Sem review")
    assert resp.status_code == 404


def test_delete_review_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_del@gmail.com", "revdel1")
    create_review(client, user["token"], "OL6060M", 1.0, "Ruim")
    resp = delete_review(client, user["token"], "OL6060M")
    assert resp.status_code == 200


def test_delete_review_not_found(client, book_user_factory):
    user = book_user_factory("rev_del_nf@gmail.com", "revdelnf1")
    resp = delete_review(client, user["token"], "OL7070M")
    assert resp.status_code == 404


def test_get_book_reviews_public(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_public@gmail.com", "revpublic1")
    create_review(client, user["token"], "OL8080M", 5.0, "Ótimo")
    resp = client.get("/api/books/reviews/OL8080M")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data


def test_get_user_reviews(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_user_list@gmail.com", "revuserlist1")
    create_review(client, user["token"], "OL9090M", 4.5, "Legal")
    resp = client.get("/api/books/reviews", headers=make_headers(user["token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
