from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health/")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "testing"
    assert isinstance(body["version"], str)


def test_health_without_trailing_slash_redirects(client: TestClient) -> None:
    response = client.get("/health", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].endswith("/health/")
