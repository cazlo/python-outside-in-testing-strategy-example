import time

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.async_job import TaskResponse
from app.core.config import settings
from app.main import app

url = "http://fastapi.localhost:1080/api/v1"
test_client = TestClient(app, base_url=url)

def test_report_job_csv():
    response = test_client.post("/auth/login", json={"email": settings.FIRST_SUPERUSER_EMAIL,
                                                     "password": settings.FIRST_SUPERUSER_PASSWORD})
    assert response.status_code == 200
    access_token = response.json()['data']['access_token']
    response = test_client.get("/report/users_list", params={
      "file_extension": "csv"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response_body = response.text
    # todo assertions on content's validity based on DB queries

def test_report_job_excel():
    response = test_client.post("/auth/login", json={"email": settings.FIRST_SUPERUSER_EMAIL,
                                                     "password": settings.FIRST_SUPERUSER_PASSWORD})
    assert response.status_code == 200
    access_token = response.json()['data']['access_token']
    response = test_client.get("/report/users_list", params={
      "file_extension": "xls"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response_body = response.text
    # todo assertions on content's validity based on DB queries