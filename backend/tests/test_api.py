from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_supports_cors():
    response = client.get(
        "/health",
        headers={"origin": "http://localhost:3000"},
    )

    assert response.headers["access-control-allow-origin"] == "*"