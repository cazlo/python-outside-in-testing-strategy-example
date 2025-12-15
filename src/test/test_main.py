import pytest
from fastapi.testclient import TestClient
from app.main import app

url = "http://fastapi.localhost:1080"
client = TestClient(app, base_url=url)

def test_root():
    response = client.get('/')
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}        

