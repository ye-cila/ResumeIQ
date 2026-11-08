"""Tests for the consistent JSON error format."""

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.exceptions import AppException
from app.main import create_app


def _client_with_test_routes() -> TestClient:
    """Build an app with extra routes that deliberately raise errors."""
    app = create_app()
    router = APIRouter(prefix="/_test")

    @router.get("/app-error")
    def raise_app_error() -> None:
        raise AppException("Resume not found", code="resume_not_found", status_code=404)

    @router.get("/crash")
    def crash() -> None:
        raise RuntimeError("secret internal detail")

    @router.get("/items/{item_id}")
    def get_item(item_id: int) -> dict:
        return {"item_id": item_id}

    app.include_router(router)
    # raise_server_exceptions=False lets us inspect the 500 response
    # instead of having TestClient re-raise the error.
    return TestClient(app, raise_server_exceptions=False)


def test_unknown_route_returns_json_404(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Not Found", "details": None}
    }


def test_method_not_allowed_returns_json_405(client: TestClient) -> None:
    response = client.post("/health/")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_app_exception_uses_its_code_and_status() -> None:
    response = _client_with_test_routes().get("/_test/app-error")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "resume_not_found",
            "message": "Resume not found",
            "details": None,
        }
    }


def test_validation_error_returns_details() -> None:
    response = _client_with_test_routes().get("/_test/items/not-a-number")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert isinstance(error["details"], list) and error["details"]


def test_unhandled_exception_hides_internal_details() -> None:
    response = _client_with_test_routes().get("/_test/crash")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"
    assert "secret internal detail" not in response.text
