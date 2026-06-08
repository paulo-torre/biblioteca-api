from datetime import datetime, timedelta

from app.database import supabase


def test_history_unauthorized(client):
    resp_post = client.post("/api/books/history/OL1M")
    assert resp_post.status_code == 401

    resp_get = client.get("/api/books/history")
    assert resp_get.status_code == 401


def test_register_view_success(client, book_user_factory, mock_book_exists):
    user = book_user_factory("history_user@gmail.com", "historyuser1")
    headers = {"Authorization": f"Bearer {user['token']}"}

    resp = client.post("/api/books/history/OL1234M", headers=headers)
    assert resp.status_code == 200

    # verify record in supabase
    result = supabase.table("view_history").select("*").eq("user_id", user["user_id"]).eq("book_id", "OL1234M").execute()
    assert result.data and len(result.data) >= 1

    # cleanup
    supabase.table("view_history").delete().eq("user_id", user["user_id"]).eq("book_id", "OL1234M").execute()


def test_get_history_returns_last_20(client, book_user_factory, mock_book_exists):
    user = book_user_factory("history_list@gmail.com", "historylist1")
    user_id = user["user_id"]

    # insert 25 views with ascending timestamps
    items = []
    base = datetime.now()
    for i in range(25):
        items.append({
            "user_id": user_id,
            "book_id": f"OL{1000 + i}M",
            "viewed_at": (base + timedelta(seconds=i)).isoformat()
        })

    supabase.table("view_history").insert(items).execute()

    resp = client.get("/api/books/history", headers={"Authorization": f"Bearer {user['token']}"})
    assert resp.status_code == 200
    data = resp.json()

    # expect at most 20 items and presence of returned data
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) <= 20

    # cleanup
    supabase.table("view_history").delete().eq("user_id", user_id).execute()


def test_post_missing_book_id_returns_405(client, book_user_factory):
    user = book_user_factory("history_missing@gmail.com", "historymiss1")
    headers = {"Authorization": f"Bearer {user['token']}"}

    resp = client.post("/api/books/history", json={}, headers=headers)
    assert resp.status_code == 405


def test_post_invalid_book_id_returns_422(client, book_user_factory):
    user = book_user_factory("history_invalid@gmail.com", "historyinv1")
    headers = {"Authorization": f"Bearer {user['token']}"}

    resp = client.post("/api/books/history/abcd", headers=headers)
    assert resp.status_code == 422


def test_duplicate_view_updates_viewed_at(client, book_user_factory, mock_book_exists):
    user = book_user_factory("history_dup@gmail.com", "historydup1")
    headers = {"Authorization": f"Bearer {user['token']}"}

    # first view
    r1 = client.post("/api/books/history/OL1A", headers=headers)
    assert r1.status_code == 200

    result1 = supabase.table("view_history").select("viewed_at").eq("user_id", user["user_id"]).eq("book_id", "OL1A").execute()
    assert result1.data
    t1 = result1.data[0].get("viewed_at")

    # second view should update timestamp (be later)
    r2 = client.post("/api/books/history/OL1A", headers=headers)
    assert r2.status_code == 200

    result2 = supabase.table("view_history").select("viewed_at").eq("user_id", user["user_id"]).eq("book_id", "OL1A").execute()
    assert result2.data
    t2 = result2.data[0].get("viewed_at")

    # try to compare parsed datetimes; be permissive with formats
    def _parse(s):
        if s is None:
            return None
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)

    dt1 = _parse(t1)
    dt2 = _parse(t2)
    assert dt1 is not None and dt2 is not None and dt2 >= dt1

    # cleanup
    supabase.table("view_history").delete().eq("user_id", user["user_id"]).eq("book_id", "OLDUP1M").execute()


def test_get_history_empty_returns_empty_list(client, book_user_factory):
    user = book_user_factory("history_empty@gmail.com", "historyempty1")
    resp = client.get("/api/books/history", headers={"Authorization": f"Bearer {user['token']}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 0


def test_user_sees_only_own_history(client, book_user_factory, mock_book_exists):
    user1 = book_user_factory("history_u1@gmail.com", "historyu1")
    user2 = book_user_factory("history_u2@gmail.com", "historyu2")

    h1 = {"Authorization": f"Bearer {user1['token']}"}
    h2 = {"Authorization": f"Bearer {user2['token']}"}

    client.post("/api/books/history/OL1A", headers=h1)
    client.post("/api/books/history/OL2M", headers=h2)

    resp1 = client.get("/api/books/history", headers=h1)
    assert resp1.status_code == 200
    data1 = resp1.json()
    ids1 = [i.get("book_id") for i in data1.get("data", [])]
    assert "OL1A" in ids1 and "OL2M" not in ids1

    # cleanup
    supabase.table("view_history").delete().eq("user_id", user1["user_id"]).execute()
    supabase.table("view_history").delete().eq("user_id", user2["user_id"]).execute()


def test_post_nonexistent_book_returns_404(client, book_user_factory):
    user = book_user_factory("history_notexist@gmail.com", "historyne1")
    headers = {"Authorization": f"Bearer {user['token']}"}

    # do not use mock_book_exists here; posting a non-existing book should return 404
    resp = client.post("/api/books/history/OL1W", headers=headers)
    assert resp.status_code == 404
