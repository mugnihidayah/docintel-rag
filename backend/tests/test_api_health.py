from fastapi.testclient import TestClient

from app.core.errors import NotFoundError
from app.main import app

client = TestClient(app)


@app.get("/_boom")
async def _boom() -> None:
    raise NotFoundError("missing thing")


def test_health_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert resp.headers["X-Request-ID"]


def test_app_error_maps_to_json() -> None:
    resp = client.get("/_boom")
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["detail"] == "missing thing"
