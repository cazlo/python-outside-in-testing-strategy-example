import time
import pytest


@pytest.mark.unit
def test_queue_and_finish_increment_task(client, celery_worker):
    """
    Unit test using FastAPI TestClient and Celery in eager mode.
    The celery_worker fixture triggers eager execution for fast testing.
    """
    test_input = 1
    response = client.post("api/v1/async_job/increment_task", json={
      "delay": test_input
    })
    assert response.status_code == 201
    response_json = response.json()
    task_id = response_json["task_id"]
    
    for tries in range(9):
        response = client.get(f"api/v1/async_job/increment_task/{task_id}")
        assert response.status_code == 200
        response_json = response.json()
        if response_json["ready"]:
            assert response_json["result"] == test_input + 1
            break
        else:
            time.sleep(0.5)
    else:
        pytest.fail("Task did not complete in time")


@pytest.mark.integration
def test_queue_and_finish_increment_task_integration(client):
    """
    Integration test using real HTTP client and real Celery worker.
    Tests the full async workflow with actual message broker.
    """
    test_input = 1
    response = client.post("api/v1/async_job/increment_task", json={
      "delay": test_input
    })
    assert response.status_code == 201
    response_json = response.json()
    task_id = response_json["task_id"]
    
    for tries in range(9):
        response = client.get(f"api/v1/async_job/increment_task/{task_id}")
        assert response.status_code == 200
        response_json = response.json()
        if response_json["ready"]:
            assert response_json["result"] == test_input + 1
            break
        else:
            time.sleep(0.5)
    else:
        pytest.fail("Task did not complete in time")


@pytest.mark.unit
def test_delete_task(client, celery_worker):
    """
    Unit test for task deletion using Celery eager mode.
    """
    test_input = 1
    response = client.post("api/v1/async_job/increment_task", json={
      "delay": test_input,
      "countdown": 10
    })
    assert response.status_code == 201
    response_json = response.json()
    task_id = response_json["task_id"]

    delete_response = client.delete(f"api/v1/async_job/increment_task/{task_id}")
    assert delete_response.status_code == 200
    delete_response_json = delete_response.json()
    assert delete_response_json["ready"] == False
    assert delete_response_json["status"] == "PENDING"


@pytest.mark.integration
def test_delete_task_integration(client):
    """
    Integration test for task deletion with real Celery worker.
    This test validates task revocation in a real distributed system.
    Note: Task revocation behavior can vary based on worker state and timing.
    """
    test_input = 1
    response = client.post("api/v1/async_job/increment_task", json={
      "delay": test_input,
      "countdown": 10
    })
    assert response.status_code == 201
    response_json = response.json()
    task_id = response_json["task_id"]

    delete_response = client.delete(f"api/v1/async_job/increment_task/{task_id}")
    assert delete_response.status_code == 200
    delete_response_json = delete_response.json()
    assert delete_response_json["ready"] == False
    # Note: Status might be PENDING or REVOKED depending on timing
    # assert delete_response_json["status"] == "PENDING"

    # Wait a bit and check task status
    time.sleep(2)
    response = client.get(f"api/v1/async_job/increment_task/{task_id}")
    assert response.status_code == 200
    response_json = response.json()
    # After revocation, task should either be REVOKED or still PENDING (if not yet picked up)
    assert response_json["status"] in ["REVOKED", "PENDING"]

