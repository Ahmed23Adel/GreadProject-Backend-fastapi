import pytest
import httpx
from unittest.mock import patch, MagicMock
from fastapi import status
import uuid
import sys
import os
import random

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import declare_location_unhealthy
from src.treatment import declare_location_unhealthy, delete_treatment_by_location

# Mock data to be returned by the mocked database call
mock_treatments = [
    {"Disease": "Disease1", "Treatment": "Treatment1"},
    {"Disease": "Disease2", "Treatment": "Treatment2"},
    {"Disease": "Disease3", "Treatment": "Treatment3"},
]

# Mock function to replace the actual database call
def mock_find():
    return mock_treatments

def test_get_default_treatment():
    """
    Objective: This test case verifies the correctness of the /get-default-treatment endpoint 
    by ensuring that it returns the default treatments for "Early_Blight" and "Late_Blight" diseases.
    Steps:
        Request Default Treatments: Sends a GET request to the /get-default-treatment endpoint with a valid authorization token to retrieve the default treatments.

        Verify Response: Checks the HTTP response status code to ensure it is 200 (OK) and validates the response JSON content.

        a. Check Success Flag: Verifies that the "success" flag in the response JSON is set to True.

        b. Check Data Presence: Ensures that the response contains a "data" field.

        c. Check Data Content: Validates that the "data" field contains default treatments for exactly two diseases.

        d. Check Disease Keys: Verifies that the response data includes default treatments for both "Early_Blight" and "Late_Blight" diseases.

    """
    
    print("Default treatment is running")
    url = "http://localhost:8000/get-default-treatment"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoZWxteSIsInVzZXJfdHlwZSI6ImV4cGVydCIsImV4cCI6MTcxNjk3Nzg5Ni44NzIxODF9.EOxd3N6sb_C0TBOavv7xHGcFTiIS9EUru55LKswjo9Q"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = httpx.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["success"] is True
    assert "data" in response_data
    assert len(response_data["data"]) == 2
    assert 'Early_Blight' in response_data["data"].keys() and 'Late_Blight' in response_data["data"].keys()


def test_update_default_treatment():
    """
    Objective: This test case verifies the functionality of updating default treatments for specific diseases, 
    ensuring that treatments are correctly modified and then restored back to their original values.
    Steps:
        Retrieve Current Default Treatments: Sends a GET request to the /get-default-treatment endpoint to fetch the current default treatments for diseases, before any updates.

        Save Old Treatments: Stores the retrieved default treatments to be used for restoration after the test.

        Update Default Treatments: Sends PUT requests to the /update-default-treatment endpoint to update the default treatments for diseases named "Early_Blight" and "Late_Blight" to new, randomly generated values.

        Verify Updates: Retrieves the default treatments again after the update and verifies that the treatments for "Early_Blight" and "Late_Blight" have been correctly updated to the new values.

        Restore Default Treatments: Sends PUT requests to the /update-default-treatment endpoint to restore the default treatments for "Early_Blight" and "Late_Blight" back to their original values saved in step 2.
            """
    # Get the current default treatments before updating
    url = "http://localhost:8000/get-default-treatment"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoZWxteSIsInVzZXJfdHlwZSI6ImV4cGVydCIsImV4cCI6MTcxNjk3Nzg5Ni44NzIxODF9.EOxd3N6sb_C0TBOavv7xHGcFTiIS9EUru55LKswjo9Q"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response_before_update = httpx.get(url, headers=headers)
    print("response_before_update", response_before_update.json())
    old_treatments = response_before_update.json()["data"]

    # Update default treatments to new values
    new_treatment = str(uuid.uuid4())
    httpx.put("http://localhost:8000/update-default-treatment",  headers = headers, params={"diseaesName": "Early_Blight", "treatment": new_treatment + "E"})
    httpx.put("http://localhost:8000/update-default-treatment",  headers = headers, params={"diseaesName": "Late_Blight", "treatment": new_treatment + "L"})

    # Check if the default treatments have been updated correctly
    response_after_update = httpx.get("http://localhost:8000/get-default-treatment", headers = headers)
    updated_treatments = response_after_update.json()["data"]

    assert updated_treatments["Early_Blight"] == new_treatment + "E"
    assert updated_treatments["Late_Blight"] == new_treatment + "L"

    # Restore default treatments back to their original values
    httpx.put("http://localhost:8000/update-default-treatment", headers = headers, params={"diseaesName": "Early_Blight", "treatment": old_treatments["Early_Blight"]})
    httpx.put("http://localhost:8000/update-default-treatment", headers = headers, params={"diseaesName": "Late_Blight", "treatment": old_treatments["Late_Blight"]})

def test_declare_location_healthy():
    """
    Objective: This test case verifies the functionality of declaring a location as healthy,
        ensuring it is correctly removed from the list of diseased locations, and then returned to 
        the list of diseased locations after being declared unhealthy again.
    Steps:
        Retrieve Diseased Locations: Fetches the list of all diseased locations from the backend using the /get-diseased-locations endpoint.

        Select Random Location: Randomly selects a location from the list of diseased locations retrieved in the previous step.

        Declare Location Healthy: Sends a request to the /declare_location_healthy endpoint to declare the randomly selected location as healthy.

        Verify Healthy Location Absence: Retrieves the list of diseased locations again and verifies that the previously selected healthy location is not present in the updated list.

        Return Location to Unhealthy State: Calls the declare_location_unhealthy function to return the previously selected location back to an unhealthy state.

        Verify Unhealthy Location Presence: Retrieves the list of diseased locations again and verifies that the previously selected location is now present in the updated list, indicating it has been returned to an unhealthy state.
            """
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoZWxteSIsInVzZXJfdHlwZSI6ImV4cGVydCIsImV4cCI6MTcxNjk3Nzg5Ni44NzIxODF9.EOxd3N6sb_C0TBOavv7xHGcFTiIS9EUru55LKswjo9Q"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response_get_locations = httpx.get("http://localhost:8000/get-diseased-locations", headers = headers)
    all_locations = response_get_locations.json()["data"]["locations"]
    print("Before:: all locations", all_locations)
    # Select a random location
    random_location = random.choice(all_locations)
    print("Randomly choose: ", random_location)
    # Declare the selected location as healthy
    httpx.put("http://localhost:8000/declare_location_healthy", params={"location": random_location, }, headers= headers)

    # Get all locations again
    response_get_locations_after = httpx.get("http://localhost:8000/get-diseased-locations", headers= headers)
    all_locations_after = response_get_locations_after.json()["data"]["locations"]
    print("After:: all locations", all_locations_after)
    # Verify that the previously healthy location is not present
    assert random_location not in all_locations_after

    # Now, return the location back to unhealthy state
    declare_location_unhealthy(random_location)

    # Get all locations after declaring unhealthy
    response_get_locations_after_unhealthy = httpx.get("http://localhost:8000/get-diseased-locations", headers = headers)
    all_locations_after_unhealthy = response_get_locations_after_unhealthy.json()["data"]["locations"]

    # Verify that the location is back to unhealthy state
    assert random_location in all_locations_after_unhealthy



def test_update_treatment_for_specific_zone():
    """This test case verifies the functionality of updating the treatment for Zone 2 and ensures that the updated treatment is correctly applied.

    """
    # Step 1: Retrieve Default Treatments
    zone_name = "Zone 2"
    url_get_default_treatment = "http://localhost:8000/get-default-treatment"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoZWxteSIsInVzZXJfdHlwZSI6ImV4cGVydCIsImV4cCI6MTcxNjk3Nzg5Ni44NzIxODF9.EOxd3N6sb_C0TBOavv7xHGcFTiIS9EUru55LKswjo9Q"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response_default_treatment = httpx.get(url_get_default_treatment, headers = headers)
    assert response_default_treatment.status_code == 200
    default_treatments = response_default_treatment.json()["data"]

    # Step 2: Store Default Treatments for Early Blight and Late Blight
    default_treatment_early_blight = default_treatments.get("Early_Blight")
    default_treatment_late_blight = default_treatments.get("Late_Blight")
    print("default_treatment_early_blight: ", default_treatment_early_blight)
    print("default_treatment_late_blight: ", default_treatment_late_blight)
    # Step 3: Retrieve Treatment for Zone 2
    url_get_treatment_for_zone_2 = "http://localhost:8000/get_treatment_value"
    params_get_treatment_for_zone_2 = {"location": zone_name}
    response_treatment_zone_2 = httpx.get(url_get_treatment_for_zone_2, params=params_get_treatment_for_zone_2, headers=headers)
    assert response_treatment_zone_2.status_code == 200
    treatment_zone_2_before_update = response_treatment_zone_2.json()["data"]["treatment"]
    print(f"Before:: For {zone_name}: treatmment = ", treatment_zone_2_before_update)
    # # Step 4: Check Treatment for Zone 2
    assert treatment_zone_2_before_update in [default_treatment_early_blight, default_treatment_late_blight]

    # # Step 5: Update Treatment for Zone 2
    new_treatment_for_zone_2 = str(uuid.uuid4())
    url_update_treatment = "http://localhost:8000/update_treatment"
    data_update_treatment = {"location": zone_name, "treatment": new_treatment_for_zone_2}
    response_update_treatment = httpx.put(url_update_treatment, params=data_update_treatment, headers=headers)
    assert response_update_treatment.status_code == 200

    # # Step 6: Retrieve Treatment for Zone 2 Again
    response_treatment_zone_2_after_update = httpx.get(url_get_treatment_for_zone_2, params=params_get_treatment_for_zone_2, headers=headers)
    assert response_treatment_zone_2_after_update.status_code == 200
    treatment_zone_2_after_update = response_treatment_zone_2_after_update.json()["data"]["treatment"]

    # # Step 7: Check Updated Treatment for Zone 2
    assert treatment_zone_2_after_update == new_treatment_for_zone_2
    print("Rolling back")
    delete_treatment_by_location(zone_name)
if __name__ == "__main__":
    # pytest.main()
    pytest.main(['-v', '--html=report.html'])
