def test_health_status_is_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_health_uptime_is_positive_number(client):
    response = client.get("/health")
    body = response.json()
    assert isinstance(body["uptime"], (int, float))
    assert body["uptime"] >= 0


def test_health_version_field_exists(client):
    response = client.get("/health")
    body = response.json()
    assert "version" in body
    assert body["version"] == "1.0.0"
