import pytest
from app_limiter import create_app


@pytest.fixture
def client():
    with create_app(prefix_subnet=str(24), delay=str(120), limit="100 per 1 minute").test_client() as client:
        return client


def exceed_limit(client):
    for x in range(100):
        response1 = client.get('/', headers={'X-Forwarded-For': '127.0.0.1'})
        assert response1.status_code == 200
    response2 = client.get('/', headers={'X-Forwarded-For': '127.0.0.1'})
    assert response2.status_code == 429
    response3 = client.get('/', headers={'X-Forwarded-For': '127.0.0.2'})
    assert response3.status_code == 429


def different_subnet(client):
    for x in range(100):
        response1 = client.get('/', headers={'X-Forwarded-For': '127.0.0.1'})
        assert response1.status_code == 200
    for x in range(100):
        response2 = client.get('/', headers={'X-Forwarded-For': '192.0.2.0'})
        assert response2.status_code == 200
