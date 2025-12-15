import pytest


@pytest.mark.unit
def test_root(client):
    response = client.get('/')
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.unit
def test_health(client):
    response = client.get('/health')
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


