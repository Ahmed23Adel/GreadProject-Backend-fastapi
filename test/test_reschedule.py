import pytest
import requests
from fastapi import status
from bson import ObjectId
from enum import Enum
from datetime import datetime, timedelta
import allure

BASE_URL = "http://localhost:8000/api/v1"

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.basic import period_of_disease_collection, treatment_schedule_collection


class RescheduleOption(str, Enum):
    DELETE_EXISTING = "delete_existing"
    KEEP_EXISTING = "keep_existing"
 
 
 
@pytest.fixture
def client():
    return requests.Session()

@pytest.fixture
def temporary_period_of_disease():
    # Create temporary data for period of disease
    period_of_disease = {
        "_id": ObjectId("665d8971ed8cfcb6c377ddc9"),
        "zoneId": ObjectId("665c7db97267b0ca7eb55003"),
        "dateCreated": datetime.strptime("2024-06-04T09:14:14.928Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
        "currentDisease": "Early blight",
        "approverExpertId": ObjectId("665c997b22e7a2373d008df8"),
        "dateApprovedByExpert": datetime.strptime("2024-06-03T09:14:14.928Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    }
    yield period_of_disease
    
    
@pytest.fixture
def temporary_treatment_schedule():
    # Create temporary data for treatment schedule
    treatment_schedule = {
        "_id": ObjectId("665dc903e3370a43a06c02ec"),
        "periodOfTreatment": ObjectId("665d8967ed8cfcb6c377ddc8"),
        "treatmentDate": datetime.strptime("2024-06-03T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
        "treatmentDesc": "Second Give water 1",
        "treatmentDone": True,
        "treatmentDoneBy": ObjectId("665c9af6604e64c0098d9627")
    }
    yield treatment_schedule
    
@pytest.fixture
def get_expert_token(client):
    url = f"{BASE_URL}/login"
    payload = {"user_name": "ahmed", "password": "12345"}
    response = client.get(url, params=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()["data"]["token"]

@allure.story("Reschedule Zone Check - DELETE_EXISTING")
def test_reschedule_zone_check_delete_existing(client, get_expert_token, temporary_period_of_disease, temporary_treatment_schedule):
    url = f"{BASE_URL}/reschedule-zone-check"
    headers = {"Authorization": f"Bearer {get_expert_token}", "Content-Type": "application/json"}
    payload = {
        "period_of_disease_id": str(temporary_period_of_disease["_id"]),
        "expert_id": str(temporary_period_of_disease["approverExpertId"]),
        "reschedule_option": RescheduleOption.DELETE_EXISTING.value
    }
    response = client.put(url, params=payload, headers=headers)
    print("response", response.content)
    print("payload", payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"]
    print("mongo",  treatment_schedule_collection.find_one({"_id": temporary_period_of_disease["_id"]}))
    # Assert that data was deleted from the collections
    assert treatment_schedule_collection.find_one({"_id": temporary_period_of_disease["_id"]}) is None

@allure.story("Reschedule Zone Check - KEEP_EXISTING")
def test_reschedule_zone_check_keep_existing(client, get_expert_token, temporary_period_of_disease, temporary_treatment_schedule):
    url = f"{BASE_URL}/reschedule-zone-check"
    headers = {"Authorization": f"Bearer {get_expert_token}", "Content-Type": "application/json"}
    payload = {
        "period_of_disease_id": str(temporary_period_of_disease["_id"]),
        "expert_id": str(temporary_period_of_disease["approverExpertId"]),
        "reschedule_option": RescheduleOption.KEEP_EXISTING.value
    }
    
    response = client.put(url, params=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"]
    
    # Assert that data still exists in the collections
    assert period_of_disease_collection.find_one({"_id": temporary_period_of_disease["_id"]}) is not None
    assert treatment_schedule_collection.find_one({"_id": temporary_treatment_schedule["_id"]}) is not None