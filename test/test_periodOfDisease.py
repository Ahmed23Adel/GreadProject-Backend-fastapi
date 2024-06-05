import pytest
import requests
from fastapi import status
import allure

BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture
def client():
    return requests.Session()

@pytest.fixture
def get_expert_token(client):
    url = f"{BASE_URL}/login"
    payload = {"user_name": "ahmed", "password": "12345"}
    response = client.get(url, params=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()["data"]["token"]

@pytest.fixture
def get_owner_token(client):
    url = f"{BASE_URL}/login"
    payload = {"user_name": "adminowner", "password": "12345"}
    response = client.get(url, params=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()["data"]["token"]

@pytest.fixture
def get_farmer_token(client):
    url = f"{BASE_URL}/login"
    payload = {"user_name": "usertmp1", "password": "12345"}
    response = client.get(url, params=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()["data"]["token"]

@pytest.fixture
def create_period_of_disease(client, get_expert_token):
    url = f"{BASE_URL}/create_period_of_disease"
    headers = {"Authorization": f"Bearer {get_expert_token}"}
    payload = {
        "currentDisease": "Early blight",
        "zoneId": "665c7db97267b0ca7eb55003",
        "dateCreated": "2023-06-01",
        "dateApprovedByExpert": None,
        "approverExpertId": None,
        "dateEnded": None,
        "enderExpertId": None,
        "specificTreatmentId": "some-treatment-id"
    }
    response = client.post(url, json=payload, headers=headers)
    print("response", payload, response.content)
    assert response.status_code == status.HTTP_200_OK
    period_of_disease_id = response.json()["data"]["id"]

    yield period_of_disease_id

    # Teardown: Delete the created period of disease
    delete_url = f"{BASE_URL}/reject_period_of_disease"
    params = {"period_of_disease_id": period_of_disease_id}
    client.delete(delete_url, headers=headers, params=params)

@allure.feature("Disease Period Management")
class TestDiseasePeriodManagement:

    @allure.story("Create Period of Disease - Success")
    def test_create_period_of_disease_success(self, client, get_expert_token):
        url = f"{BASE_URL}/create_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        payload = {
            "currentDisease": "Early blight",
            "zoneId": "665c7db97267b0ca7eb55003",
            "dateCreated": "2023-06-01",
            "dateApprovedByExpert": None,
            "approverExpertId": None,
            "dateEnded": None,
            "enderExpertId": None,
            "specificTreatmentId": "some-treatment-id"
        }
        response = client.post(url, json=payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"]

        # Teardown
        period_of_disease_id = response.json()["data"]["id"]
        delete_url = f"{BASE_URL}/reject_period_of_disease"
        params = {"period_of_disease_id": period_of_disease_id}
        client.delete(delete_url, headers=headers, params=params)

    @allure.story("Create Period of Disease - Already Open Period")
    def test_create_period_of_disease_already_open(self, client, get_expert_token, create_period_of_disease):
        url = f"{BASE_URL}/create_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        payload = {
            "currentDisease": "Late blight",
            "zoneId": "665c7db97267b0ca7eb55002",
            "dateCreated": "2023-06-15",
            "dateApprovedByExpert": None,
            "approverExpertId": None,
            "dateEnded": None,
            "enderExpertId": None,
            "specificTreatmentId": "some-treatment-id"
        }
        response = client.post(url, json=payload, headers=headers)
        print("response", payload, response.content)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "There is already an open period of disease for the given zoneId"

    @allure.story("Reject Period of Disease - Success")
    def test_reject_period_of_disease_success(self, client, get_expert_token, create_period_of_disease):
        url = f"{BASE_URL}/reject_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        params = {"period_of_disease_id": create_period_of_disease}
        response = client.delete(url, headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"]

        # Verify the period of disease does not appear in open zones
        url = f"{BASE_URL}/get-diseased-zones"
        response = client.get(url, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        diseased_zones = response.json()["data"]["locations"]
        assert all(zone["activePeriodOfDisease"] != create_period_of_disease for zone in diseased_zones)

    @allure.story("Reject Period of Disease - Already Approved")
    def test_reject_period_of_disease_already_approved(self, client, get_expert_token):
        url = f"{BASE_URL}/reject_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        approved_period_id = "665d8967ed8cfcb6c377ddc1"  # This should be an ID of an already approved period in your database
        params = {"period_of_disease_id": approved_period_id}
        response = client.delete(url, headers=headers, params=params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Cannot reject an approved period of disease"

    @allure.story("Reject Period of Disease - Unauthorized User")
    def test_reject_period_of_disease_unauthorized(self, client, get_owner_token, create_period_of_disease):
        url = f"{BASE_URL}/reject_period_of_disease"
        headers = {"Authorization": f"Bearer {get_owner_token}"}
        params = {"period_of_disease_id": create_period_of_disease}
        response = client.delete(url, headers=headers, params=params)
        print("responsedel", response.content, response.status_code)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @allure.story("Reject Period of Disease - Not Found")
    def test_reject_period_of_disease_not_found(self, client, get_expert_token):
        url = f"{BASE_URL}/reject_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        params = {"period_of_disease_id": "665d8961ed8cfcb6c399ddc9"}
        response = client.delete(url, headers=headers, params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Period of disease not found"
