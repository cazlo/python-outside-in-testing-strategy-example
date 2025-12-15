import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

url = "http://fastapi.localhost:1080/api/v1"
test_client = TestClient(app, base_url=url)

class TestPostLogin:
    @pytest.mark.parametrize(
        "method, endpoint, data, expected_status, expected_response",
        [
            ("post", "/auth/login", {"email": "incorrect_email@gmail.com", "password": "123456"}, 401, {"detail": "Email or Password incorrect"}),
            ("post", "/auth/login", {"email": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD}, 200, None),
            ("post", "/auth/login", {"email": settings.FIRST_SUPERUSER_EMAIL, "password": "foobar"}, 401, None),
            ("post", "/auth/login", {"email": "user@example.com", "password": settings.FIRST_SUPERUSER_PASSWORD}, 403, None),
            ("post", "/auth/new_access_token", {"refresh_token": ""}, 403, {"detail": "Error when decoding the token. Please check your request."})
        ],
    )
    def test(self, method, endpoint, data, expected_status, expected_response):
            if method == "get":
                response = test_client.get(endpoint)
            elif method == "put":
                response = test_client.put(endpoint, json=data)
            elif method == "delete":
                response = test_client.delete(endpoint)
            else:  # Default to POST
                response = test_client.post(endpoint, json=data)

            assert response.status_code == expected_status
            if expected_response is not None:                
                assert response.json() == expected_response

    def test_login_logout(self):
        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer none"})
        assert user_list_response.status_code == 403

        response = test_client.post("/auth/login", json={"email": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD})
        assert response.status_code == 200
        access_token = response.json()['data']['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        response = test_client.post("/auth/logout", json={}, headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200

        new_user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert new_user_list_response.status_code == 403

    def test_login_logout_via_access_token(self):
        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer none"})
        assert user_list_response.status_code == 403

        response = test_client.post("/auth/access-token", data={"username": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD})
        assert response.status_code == 200
        access_token = response.json()['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        response = test_client.post("/auth/logout", json={}, headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200

        new_user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert new_user_list_response.status_code == 403

    def test_get_new_token_from_refresh_token(self):
        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer none"})
        assert user_list_response.status_code == 403

        response = test_client.post("/auth/login", json={"email": settings.FIRST_SUPERUSER_EMAIL,
                                                         "password": settings.FIRST_SUPERUSER_PASSWORD})
        assert response.status_code == 200
        access_token = response.json()['data']['access_token']
        refresh_token = response.json()['data']['refresh_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        refresh_token_response = test_client.post("/auth/new_access_token", json={"refresh_token":refresh_token})
        assert refresh_token_response.status_code == 201
        new_access_token = response.json()['data']['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {new_access_token}"})
        assert user_list_response.status_code == 200

    def test_login_logout(self):
        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer none"})
        assert user_list_response.status_code == 403

        response = test_client.post("/auth/login", json={"email": settings.FIRST_SUPERUSER_EMAIL, "password": settings.FIRST_SUPERUSER_PASSWORD})
        assert response.status_code == 200
        access_token = response.json()['data']['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        response = test_client.post("/auth/logout", json={}, headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200

        new_user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert new_user_list_response.status_code == 403

    def test_login_and_change_password(self):
        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer none"})
        assert user_list_response.status_code == 403

        response = test_client.post("/auth/login", json={"email": "manager@example.com", "password": settings.FIRST_SUPERUSER_PASSWORD})
        assert response.status_code == 200
        access_token_original = response.json()['data']['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token_original}"})
        assert user_list_response.status_code == 200

        new_password = "new_pass"

        response = test_client.post("/auth/change_password", json={
          "current_password": settings.FIRST_SUPERUSER_PASSWORD,
          "new_password": new_password,
        }, headers={"Authorization": f"Bearer {access_token_original}"})
        assert response.status_code == 200

        new_user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token_original}"})

        response = test_client.post("/auth/login", json={"email": "manager@example.com", "password": new_password})
        assert response.status_code == 200
        access_token = response.json()['data']['access_token']

        user_list_response = test_client.get("/user/list", headers={"Authorization": f"Bearer {access_token}"})
        assert user_list_response.status_code == 200

        response = test_client.post("/auth/change_password", json={
            "current_password": new_password,
            "new_password": settings.FIRST_SUPERUSER_PASSWORD,
        }, headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200

        assert new_user_list_response.status_code == 403