from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_watermark_not_found():
    response = client.get(
        "/exports/watermark",
        headers={"X-Consumer-ID": "non-existent-consumer"}
    )
    assert response.status_code == 404