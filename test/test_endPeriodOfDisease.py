import pytest
import requests
from fastapi import status
from bson import ObjectId
from datetime import datetime
import allure

BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture
def client():
    return requests.Session()

@pytest.fixture
def temporary_period_of_disease():
    # Define the temporary period of disease document
    period_of_disease = {
        "_id": ObjectId("665d8971ed8cfcb6c377ddc9"),
        "zoneId": ObjectId("665c7db97267b0ca7eb55003"),
        "dateCreated": datetime(2024, 6, 4, 9, 14, 14, 928000),
        "currentDisease": "Early blight"
    }
    yield period_of_disease

@pytest.fixture
def get_expert_token(client):
    url = f"{BASE_URL}/login"
    payload = {"user_name": "ahmed", "password": "12345"}
    response = client.get(url, params=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()["data"]["token"]

@allure.feature("Period of Disease Management")
class TestEndPeriodOfDisease:

    

    @allure.story("End Period of Disease - Not Approved")
    def test_end_period_of_disease_not_approved(self, client, get_expert_token):
        url = f"{BASE_URL}/end_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        payload = {
            "period_of_disease_id": "665d8971ed8cfcb6c377ddc9",
            "ender_expert_id": "665c997b22e7a2373d008df8"
        }
        response = client.put(url, params=payload, headers=headers)
        print("response", response.content)
        assert response.status_code == 400
        print(response.json())
        assert response.json()["detail"] == "The period of disease is not open, approved, or does not exist"

    @allure.story("End Period of Disease - Already Ended")
    def test_end_period_of_disease_already_ended(self, client, get_expert_token):
        url = f"{BASE_URL}/end_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        payload = {
            "period_of_disease_id": "665d8967ed8cfcb6c377ddc6",
            "ender_expert_id": "665c997b22e7a2373d008df8"
        }
        response = client.put(url, json=payload, headers=headers)
        assert response.status_code == 422

    @allure.story("End Period of Disease - Period Not Found")
    def test_end_period_of_disease_period_not_found(self, client, get_expert_token):
        url = f"{BASE_URL}/end_period_of_disease"
        headers = {"Authorization": f"Bearer {get_expert_token}"}
        payload = {
            "period_of_disease_id": "665d8967ed8cfcb6c888ddc6",
            "ender_expert_id": "665c997b22e7a2373d008df8"
        }
        response = client.put(url, json=payload, headers=headers)
        assert response.status_code == 422
