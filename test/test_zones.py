import allure
import pytest
import requests
from fastapi import status

@pytest.fixture
def client():
    return requests.Session()

@allure.feature("Hardware Authentication")
class TestHardwareAuthentication:
    
    @allure.story("Successful Login")
    def test_login_hardware_success(self, client):
        url = "http://localhost:8000/api/v1/login-hardware/"
        payload = {"user_name": "hardwareadmin", "password": "12345"}
        response = client.get(url, params=payload)
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.json()["data"]

    @allure.story("Incorrect Credentials")
    def test_login_hardware_incorrect_credentials(self, client):
        url = "http://localhost:8000/api/v1/login-hardware/"
        payload = {"user_name": "hardwareadmin", "password": "wrong_password"}
        response = client.get(url, params=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
@allure.feature("Zone Management")
class TestZoneManagement:

    @pytest.fixture
    def created_zone(self, client):
        # Login to obtain token
        login_url = "http://localhost:8000/api/v1/login-hardware/"
        login_payload = {"user_name": "hardwareadmin", "password": "12345"}
        login_response = client.get(login_url, params=login_payload)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["data"]["token"]
        
        # Create new zone
        url = "http://localhost:8000/api/v1/create-new-zone"
        zone_data = {"zone_name": "Zone 1000"}
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(url, json=zone_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

        yield {"zone_name": "Zone 1000"}

        # Teardown: Delete the created zone
        delete_url = f"http://localhost:8000/api/v1/delete-zone"
        delete_payload = {"zone_name": "Zone 1000"}
        response = client.post(delete_url, json=delete_payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK

    # @allure.story("Create New Zone - Success")
    # def test_create_new_zone_success(self, client, created_zone):
    #     # No assertion needed here, as the fixture already verified creation
    #     pass

    @allure.story("Create New Zone - Duplicate Name")
    def test_create_new_zone_duplicate_name(self, client):
        # Login to obtain token
        login_url = "http://localhost:8000/api/v1/login-hardware/"
        login_payload = {"user_name": "hardwareadmin", "password": "12345"}
        login_response = client.get(login_url, params=login_payload)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["data"]["token"]
        
        # Attempt to create a zone with duplicate name
        url = "http://localhost:8000/api/v1/create-new-zone"
        zone_data = {"zone_name": "Zone 1"}  # Existing zone name
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(url, json=zone_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Zone name already exists"

    @allure.story("Create New Zone - Invalid Zone Name Format")
    def test_create_new_zone_invalid_name_format(self, client):
        # Login to obtain token
        login_url = "http://localhost:8000/api/v1/login-hardware/"
        login_payload = {"user_name": "hardwareadmin", "password": "12345"}
        login_response = client.get(login_url, params=login_payload)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["data"]["token"]
        
        # Attempt to create a zone with invalid name format
        url = "http://localhost:8000/api/v1/create-new-zone"
        zone_data = {"zone_name": "Invalid Zone Name"}  # Invalid format
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(url, json=zone_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Invalid zone name format. Zone name must be in the format 'Zone x' where 'x' is an integer."

    # Add more test cases as needed...
