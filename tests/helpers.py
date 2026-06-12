import bcrypt

from app.services.database import supabase
from app.dependencies import create_access_token

_to_cleanup = []

def register_and_verify(client, email, username, password):
    client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": password
    })
    result = supabase.table("users").select("verify_code").eq("email", email).execute()
    code = result.data[0]["verify_code"]
    response = client.post("/api/auth/verify-email", json={"email": email, "code": code})

    if email not in _to_cleanup:
        _to_cleanup.append(email)

    return response.json()["access_token"]


def make_headers(token):
    return {"Authorization": f"Bearer {token}"}


def cleanup_user(email):
    supabase.table("users").delete().eq("email", email).execute()
    if email in _to_cleanup:
        try:
            _to_cleanup.remove(email)
        except ValueError:
            pass


def get_user_id(email):
    result = supabase.table("users").select("id").eq("email", email).execute()
    if not result.data:
        return None
    return result.data[0]["id"]


def cleanup_book_data(user_id, book_id=None):
    if not user_id:
        return

    for table in ("saved_books", "book_opinions", "book_reviews"):
        query = supabase.table(table).delete().eq("user_id", user_id)
        if book_id:
            query = query.eq("book_id", book_id)
        query.execute()


def cleanup_book_test_user(email):
    user_id = get_user_id(email)
    cleanup_book_data(user_id)
    cleanup_user(email)


def create_verified_user(email, username, password="Senha123!"):
    cleanup_book_test_user(email)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    result = supabase.table("users").insert({
        "email": email,
        "username": username,
        "password": hashed,
        "email_verified": True,
    }).execute()

    user = result.data[0]
    token = create_access_token(
        user_id=user["id"],
        email=email,
        username=username
    )

    if email not in _to_cleanup:
        _to_cleanup.append(email)

    return {
        "email": email,
        "username": username,
        "password": password,
        "token": token,
        "headers": make_headers(token),
        "user_id": user["id"],
    }


class _NoopAwaitable:
    def __await__(self):
        if False:
            yield
        return None


def mock_validate_book_exists(monkeypatch):
    from app.routers import books as books_router

    def fake_validate_book_exists(book_id):
        return _NoopAwaitable()

    monkeypatch.setattr(books_router, "validate_book_exists", fake_validate_book_exists)


def save_book(client, token, book_id):
    return client.post(
        f"/api/books/saved/{book_id}",
        headers=make_headers(token)
    )


def delete_saved_book(client, token, book_id):
    return client.request(
        "DELETE",
        f"/api/books/saved/{book_id}",
        json={"book_id": book_id},
        headers=make_headers(token)
    )


def create_opinion(client, token, book_id, opinion="liked"):
    return client.post(
        "/api/books/opinions",
        json={"book_id": book_id, "opinion": opinion},
        headers=make_headers(token)
    )


def update_opinion(client, token, book_id, opinion):
    return client.put(
        "/api/books/opinions",
        json={"book_id": book_id, "opinion": opinion},
        headers=make_headers(token)
    )


def delete_opinion(client, token, book_id):
    return client.request(
        "DELETE",
        f"/api/books/opinions/{book_id}",
        json={"book_id": book_id},
        headers=make_headers(token)
    )


def create_review(client, token, book_id, rating=4.5, comment="Review de teste"):
    payload = {"book_id": book_id, "rating": rating}
    if comment is not None:
        payload["comment"] = comment

    return client.post(
        "/api/books/reviews",
        json=payload,
        headers=make_headers(token)
    )


def update_review(client, token, book_id, rating=4.0, comment="Review atualizada"):
    payload = {"book_id": book_id, "rating": rating}
    if comment is not None:
        payload["comment"] = comment

    return client.put(
        "/api/books/reviews",
        json=payload,
        headers=make_headers(token)
    )


def delete_review(client, token, book_id):
    return client.request(
        "DELETE",
        f"/api/books/reviews/{book_id}",
        json={"book_id": book_id},
        headers=make_headers(token)
    )
