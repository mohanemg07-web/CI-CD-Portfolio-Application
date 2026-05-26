def test_metrics_endpoint_returns_200(client):
    # Touch other routes so counters are populated.
    client.get("/health")
    client.get("/projects")
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_contains_http_requests_total(client):
    client.get("/health")
    response = client.get("/metrics")
    assert "http_requests_total" in response.text


def test_metrics_contains_app_uptime_gauge(client):
    response = client.get("/metrics")
    assert "app_uptime_seconds" in response.text
