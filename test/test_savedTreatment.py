import pytest
import requests
from fastapi import status
import sys
import os
import allure

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.basic import saved_treatment_schedule_collection, saved_treatment_schedule_itmes_collection, app

BASE_URL = "http://localhost:8000/api/v1"

def delete_test_data():
    saved_treatment_schedule_collection.delete_many({"treatmentName": {"$regex": "Test Treatment|Duplicate Treatment|Incomplete Treatment|Invalid Treatment|Unauthorized Test"}})

@pytest.fixture
def get_token():
    # Static token values for expert, owner, and farmer
    return {
        "ahmed": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZCIsInVzZXJfdHlwZSI6ImV4cGVydCIsInVzZXJfaWQiOiI2NjVjOTk3YjIyZTdhMjM3M2QwMDhkZjgiLCJleHAiOjE3MTc2MjIwNzcuMzI2MjM2fQ.j5CvG5id8WRZUF-98k1URqF1KT4VPwMQVLYBJfzMchQ",
        "adminowner": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbm93bmVyIiwidXNlcl90eXBlIjoib3duZXIiLCJ1c2VyX2lkIjoiNjY1Yzk4NmNkYjI1ZjljNzY5MTBlNjQwIiwiZXhwIjoxNzE3NjIyMDM5LjU5MDU1NH0.-gOPYKp_ejmF_DphlYaQY34_X9ga4AjGYEkNMunAhSY",
        "usertmp1": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VydG1wMSIsInVzZXJfdHlwZSI6ImZhcm1lciIsInVzZXJfaWQiOiI2NjVkZjYwMDY1NTBlZjJlYTg0MmZmMWEiLCJleHAiOjE3MTc2MjIwNjEuMDExMDc0fQ.gCugWVUwPoYqAzUBDV9h14F9u5FqJAvpVHCF_9OQUgs"
    }

@pytest.fixture
def client():
    return requests.Session()

@allure.feature('Treatment Schedule')
@allure.story('Create New Schedule')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description('Test case to verify successful creation of a new treatment schedule.')
def test_create_saved_treatment_schedule_success(client, get_token):
    token = get_token["ahmed"]

    new_schedule = {
        "treatmentName": "Test Treatment",
        "treatmentDescription": "Test Description",
        "treatmentItems": [
            {"dayNumber": 1, "dayTreatment": "Treatment A"},
            {"dayNumber": 2, "dayTreatment": "Treatment B"}
        ]
    }

    with allure.step("Sending POST request to create new treatment schedule"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content"):
        print("response",response.content )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] == True
        assert "data" in response.json()

    delete_test_data()

@allure.feature('Treatment Schedule')
@allure.story('Create Duplicate Schedule')
@allure.severity(allure.severity_level.NORMAL)
@allure.description('Test case to verify behavior when creating a schedule with a duplicate name.')
def test_create_saved_treatment_schedule_duplicate_name(client, get_token):
    token = get_token["ahmed"]

    existing_schedule = {
        "treatmentName": "Duplicate Treatment",
        "treatmentDescription": "Existing Description",
        "treatmentItems": []
    }

    saved_treatment_schedule_collection.insert_one(existing_schedule)

    new_schedule = {
        "treatmentName": "Duplicate Treatment",
        "treatmentDescription": "New Description",
        "treatmentItems": [
            {"dayNumber": 1, "dayTreatment": "Treatment A"},
            {"dayNumber": 2, "dayTreatment": "Treatment B"}
        ]
    }

    with allure.step("Sending POST request to create a duplicate treatment schedule"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content for duplicate name"):
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "A treatment schedule with the same name already exists."

    delete_test_data()

@allure.feature('Treatment Schedule')
@allure.story('Create Schedule with Missing Data')
@allure.severity(allure.severity_level.MINOR)
@allure.description('Test case to verify behavior when creating a schedule with missing data.')
def test_create_saved_treatment_schedule_missing_data(client, get_token):
    token = get_token["ahmed"]

    new_schedule = {
        "treatmentName": "Incomplete Treatment",
        # Missing description and treatmentItems
    }

    with allure.step("Sending POST request to create a schedule with missing data"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content for missing data"):
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    delete_test_data()

@allure.feature('Treatment Schedule')
@allure.story('Create Schedule with Invalid Data')
@allure.severity(allure.severity_level.MINOR)
@allure.description('Test case to verify behavior when creating a schedule with invalid data.')
def test_create_saved_treatment_schedule_invalid_data(client, get_token):
    token = get_token["ahmed"]

    new_schedule = {
        "treatmentName": "Invalid Treatment",
        "treatmentDescription": "Invalid Description",
        "treatmentItems": [
            {"dayNumber": "One", "dayTreatment": "Treatment A"}  # dayNumber should be an integer
        ]
    }

    with allure.step("Sending POST request to create a schedule with invalid data"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content for invalid data"):
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    delete_test_data()

@allure.feature('Treatment Schedule')
@allure.story('Unauthorized Creation by Owner')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description('Test case to verify unauthorized creation of a treatment schedule by an owner.')
def test_create_saved_treatment_schedule_unauthorized_owner(client, get_token):
    token = get_token["adminowner"]

    new_schedule = {
        "treatmentName": "Unauthorized Test",
        "treatmentDescription": "Unauthorized Description",
        "treatmentItems": [
            {"dayNumber": 1, "dayTreatment": "Treatment A"},
            {"dayNumber": 2, "dayTreatment": "Treatment B"}
        ]
    }

    with allure.step("Sending POST request to create a schedule by an unauthorized owner"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content for unauthorized owner"):
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    delete_test_data()

@allure.feature('Treatment Schedule')
@allure.story('Unauthorized Creation by Farmer')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description('Test case to verify unauthorized creation of a treatment schedule by a farmer.')
def test_create_saved_treatment_schedule_unauthorized_farmer(client, get_token):
    token = get_token["usertmp1"]

    new_schedule = {
        "treatmentName": "Unauthorized Test",
        "treatmentDescription": "Unauthorized Description",
        "treatmentItems": [
            {"dayNumber": 1, "dayTreatment": "Treatment A"},
            {"dayNumber": 2, "dayTreatment": "Treatment B"}
        ]
    }

    with allure.step("Sending POST request to create a schedule by an unauthorized farmer"):
        response = client.post(
            f"{BASE_URL}/create_saved_treatment_schedule/",
            json=new_schedule,
            headers={"Authorization": f"Bearer {token}"}
        )

    with allure.step("Asserting response status and content for unauthorized farmer"):
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    delete_test_data()
