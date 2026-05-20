import httpx


class FakeResponse:
    def __init__(self, data=None, status_code=200, raise_error=False):
        self._data = data or {}
        self.status_code = status_code
        self._raise_error = raise_error

    def json(self):
        return self._data

    def raise_for_status(self):
        if self._raise_error:
            raise httpx.HTTPError("error")


class FakeClient:
    def __init__(self, behaviour):
        self.behaviour = behaviour

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        # behaviour is a dict describing what to return for search
        if self.behaviour.get("raise_request_error"):
            raise httpx.RequestError("request failed")

        return FakeResponse(data=self.behaviour.get("data", {}), status_code=200)


def test_search_success(monkeypatch, client):
    behaviour = {
        "data": {
            "docs": [
                {"key": "OL1M", "title": "Livro A", "author_name": ["Autor X"], "first_publish_year": 2000, "cover_i": 123}
            ]
        }
    }

    def _fake_factory(*args, **kwargs):
        return FakeClient(behaviour)

    monkeypatch.setattr(httpx, "AsyncClient", _fake_factory)

    response = client.request("GET", "/api/books/search/qualquer")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_empty_query_returns_400(client):
    response = client.request("GET", "/api/books/search/   ")
    assert response.status_code == 400


def test_search_openlibrary_request_error(monkeypatch, client):
    behaviour = {"raise_request_error": True}

    def _fake_factory(*args, **kwargs):
        return FakeClient(behaviour)

    monkeypatch.setattr(httpx, "AsyncClient", _fake_factory)

    response = client.request("GET", "/api/books/search/qualquer")
    assert response.status_code == 503
