import time

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.async_job import TaskResponse
from app.main import app

url = "http://fastapi.localhost:1080/api/v1"
test_client = TestClient(app, base_url=url)

def test_queue_and_finish_increment_task(celery_worker):
    test_input = 1
    response = test_client.post("async_job/increment_task", json={
      "delay": test_input
    })
    assert response.status_code == 201
    response_body = TaskResponse(**response.json())
    task_id = response_body.task_id
    for tries in range(9):
        response = test_client.get(f"async_job/increment_task/{task_id}")
        assert response.status_code == 200
        response_body = TaskResponse(**response.json())
        if response_body.ready:
            assert response_body.result == test_input + 1
        else:
            time.sleep(0.5)


def test_delete_task(celery_worker):
    test_input = 1
    response = test_client.post("async_job/increment_task", json={
      "delay": test_input,
      "countdown": 10
    })
    assert response.status_code == 201
    response_body = TaskResponse(**response.json())
    task_id = response_body.task_id

    delete_response = test_client.delete(f"async_job/increment_task/{task_id}")
    assert delete_response.status_code == 200
    delete_response_body = TaskResponse(**delete_response.json())
    assert delete_response_body.ready == False
    assert delete_response_body.status == "PENDING"

    # todo the following is only working for integration tests using non-embedded celery_worker
    # response = test_client.get(f"async_job/increment_task/{task_id}")
    # assert response.status_code == 200
    # response_body = TaskResponse(**response.json())
    # assert response_body.status == "REVOKED"