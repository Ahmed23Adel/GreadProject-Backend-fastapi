import pytest
import httpx
from unittest.mock import patch, MagicMock
from fastapi import status
import uuid
import sys
import os
import random

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZCIsInVzZXJfdHlwZSI6Im93bmVyIiwiZXhwIjoxNzE2OTk1Mjk0LjA0MDgzMn0.dbXfbzcNcrzx-UhbqJFlTsikwx2KZb1JyJzDkDOXMEc"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.basic import user_collection, images_collection

def test_create_new_images():
    expert_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZDEiLCJ1c2VyX3R5cGUiOiJleHBlcnQiLCJleHAiOjE3MTcwMTQwNzcuNzc4NjE3fQ.WlN0EuWOpX4NUseltJdaryEA53twFIVwPBGFPWA-Z-4"
    headers_exeprt = {
        "Authorization": f"Bearer {expert_token}"
    }
    # Dummy data for 20 images
    # Disease by treated and classificatoin =2
    # 12 of them must be diseased
    images_data = []
    # diseased and edited
    for i in range(2):
        images_data.append(
            {"Image_Path": "path1", "Location": "Zone 3", "Date": "2050-01-01", "Time": "12:00:00",
            "Classification": [2]*5, "Confidence": [0.99]*5, "bbox": [], "Image_Class": 1, "Edited": True, "Treated": False,
            "Resized_Path": "resized_path1", "Annotated_Path": "annotated_path1"}
        )
    # only diseased
    for i in range (10):
        images_data.append(
            {"Image_Path": "path1", "Location": "Zone 3", "Date": "2050-01-01", "Time": "12:00:00",
            "Classification": [2]*5, "Confidence": [0.99]*5, "bbox": [], "Image_Class": 1, "Edited": False, "Treated": False,
            "Resized_Path": "resized_path1", "Annotated_Path": "annotated_path1"}
        )


    # 8 must be not diseased
    # diseased and not edited
    # image class not 0,1 then not diseased
    for _ in range(2):
        classification = random.choice([1,2])
        images_data.append(
            {"Image_Path": "path1", "Location": "Zone 3", "Date": "2050-01-01", "Time": "12:00:00",
            "Classification": [classification]*5, "Confidence": [0.99]*5, "bbox": [], "Image_Class": 2, "Edited": True, "Treated": True,
            "Resized_Path": "resized_path1", "Annotated_Path": "annotated_path1"}
        )
    for i in range (6):
        
        classification = random.choice([1,2])
        images_data.append(
            {"Image_Path": "path1", "Location": "Zone 3", "Date": "2050-01-01", "Time": "12:00:00",
            "Classification": [classification]*5, "Confidence": [0.99]*5, "bbox": [], "Image_Class": 2, "Edited": False, "Treated": True,
            "Resized_Path": "resized_path1", "Annotated_Path": "annotated_path1"}
        )

    expert_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZDEiLCJ1c2VyX3R5cGUiOiJleHBlcnQiLCJleHAiOjE3MTcwMTQwNzcuNzc4NjE3fQ.WlN0EuWOpX4NUseltJdaryEA53twFIVwPBGFPWA-Z-4"
    headers_exeprt = {
        "Authorization": f"Bearer {expert_token}"
    }
    

# Make the POST request with the payload
    for image_data in images_data:
        response = httpx.post("http://localhost:8000/images/create/", json=image_data, headers=headers_exeprt)
        assert response.status_code == 200
        assert response.json()["success"] is True

    expected_count = 20
    expected_percentage_diseased = 12 * 100 / 20
    expected_percentage_diseased_after_mod = 2 * 100 / 20
    expected_mod_rate = 2*100 / 12
    response = httpx.get("http://localhost:8000/latest_pics", headers = headers_exeprt)
    assert response.status_code == 200
    data = response.json()
    latest_date = data["data"]["latest_date"]
    count = data["data"]["count"]
    percentage_diseased = data["data"]["percentage_diseased"]
    percentage_diseased_after_mod = data["data"]["percentage_diseased_after_mod"]
    mod_rate = data["data"]["mod_rate"]
    assert count == expected_count
    assert percentage_diseased == expected_percentage_diseased
    assert percentage_diseased_after_mod == expected_percentage_diseased_after_mod
    assert abs(mod_rate - expected_mod_rate) < 1e-6
    filter_query = {"Date": "2050-01-01"}
    # Delete documents matching the filter query
    delete_result = images_collection.delete_many(filter_query)
    # Print the number of deleted documents
    print(f"Number of deleted documents: {delete_result.deleted_count}")







if __name__ == "__main__":
    pytest.main()