from tests.helpers import create_review, delete_review, make_headers, update_review


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

def test_get_book_reviews_public_pagination(client, book_user_factory, mock_book_exists):
    for i in range(3):
        user = book_user_factory(f"rev_public_pag{i+1}@gmail.com", f"revpublic_pag{i+1}")
        create_review(client, user["token"], "OL8080M", 2.5, "Meh")

    user = book_user_factory(
        "rev_public_pag@gmail.com", "revpublic_pag"
    )
    resp = client.get(
        "/api/books/reviews/OL8080M?page=1&size=2", headers=make_headers(user["token"])
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 2


def test_get_book_reviews_public_pagination_invalid_size(client, book_user_factory, mock_book_exists):
    user = book_user_factory("revpublic_invalid_lmt@gmail.com", "revpublic_invalid_lmt1")
    create_review(client, user["token"], "OL8080M", 4.5, "Muito bom")
    resp = client.get(
        "/api/books/reviews/OL8080M?size=999",
        headers=make_headers(user["token"])
    )
    assert resp.status_code == 422

def test_get_book_reviews_public_pagination_invalid_page(client, book_user_factory, mock_book_exists):
    user = book_user_factory("revpublic_invalidpage@gmail.com", "revpublic_invalidpage1")
    create_review(client, user["token"], "OL8080M", 4.5, "Muito bom")
    resp = client.get(
        "/api/books/reviews/OL8080M?page=0",
        headers=make_headers(user["token"])
    )
    assert resp.status_code == 422


def test_get_user_reviews(client, book_user_factory, mock_book_exists):
    user = book_user_factory("rev_user_list@gmail.com", "revuserlist1")
    create_review(client, user["token"], "OL9090M", 4.5, "Legal")
    resp = client.get("/api/books/reviews", headers=make_headers(user["token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data


def test_get_book_reviews_pagination(client, book_user_factory, mock_book_exists):
    for i in range(3):
        user = book_user_factory(
            f"review_pag{i + 1}@gmail.com",f"review_pag{i + 1}"
        )
        create_review(client, user["token"], "OL8080M", i, "Ruim")

    user = book_user_factory("review_pag@gmail.com", "review_pag")
    resp = client.get(
        "/api/books/reviews?page=1&size=2", headers=make_headers(user["token"])
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 2


def test_get_book_reviews_pagination_invalid_size(client, book_user_factory, mock_book_exists):
    user = book_user_factory(
        "review_invalid_lmt@gmail.com", "review_invalid_lmt1"
    )
    create_review(client, user["token"], "OL8080M", 4.5, "Muito bom")
    resp = client.get(
        "/api/books/reviews?size=999", headers=make_headers(user["token"])
    )
    assert resp.status_code == 422


def test_get_book_reviews_pagination_invalid_page(client, book_user_factory, mock_book_exists):
    user = book_user_factory(
        "review_invalidpage@gmail.com", "review_invalidpage1"
    )
    create_review(client, user["token"], "OL8080M", 4.5, "Muito bom")
    resp = client.get("/api/books/reviews?page=0", headers=make_headers(user["token"]))
    assert resp.status_code == 422
