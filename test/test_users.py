import pytest
import httpx
from unittest.mock import patch, MagicMock
from fastapi import status
import uuid
import sys
import os
import random

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZCIsInVzZXJfdHlwZSI6Im93bmVyIiwiZXhwIjoxNzE2OTk1Mjk0LjA0MDgzMn0.dbXfbzcNcrzx-UhbqJFlTsikwx2KZb1JyJzDkDOXMEc"

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import declare_location_unhealthy
from src.basic import user_collection


def generate_random_user(user_type = "expert"):
    user_name = str(uuid.uuid4())
    password = "testpassword"
    return {"user_name": user_name, "password": password, "type": user_type}

def test_activate_only_experts():
    # Step 1: Create an "expert" user and an "owner" user
    expert_user_data = generate_random_user("expert")
    owner_user_data = generate_random_user("owner")
    
    response_expert = httpx.post("http://localhost:8000/register/", params=expert_user_data)
    assert response_expert.status_code == 200
    assert response_expert.json()["success"] is True
    
    response_owner = httpx.post("http://localhost:8000/register/", params=owner_user_data)
    assert response_owner.status_code == 200
    assert response_owner.json()["success"] is True
    
    expert_user = user_collection.find_one({"user_name": expert_user_data["user_name"]})
    owner_user = user_collection.find_one({"user_name": owner_user_data["user_name"]})
    
    expert_user_id = str(expert_user["_id"])
    owner_user_id = str(owner_user["_id"])
    
    # Step 2: Attempt to activate both users
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response_activate_expert = httpx.put(
        "http://localhost:8000/activate_user/", 
        params={"user_id": expert_user_id, "activated": True},
        headers=headers
    )
    response_activate_owner = httpx.put(
        "http://localhost:8000/activate_user/", 
        params={"user_id": owner_user_id, "activated": True},
        headers=headers
    )
    
    # Step 3: Verify activation results
    assert response_activate_expert.status_code == 200
    assert response_activate_expert.json()["success"] is True
    assert response_activate_expert.json()["data"]["activated"] is True
    
    assert response_activate_owner.status_code == 403
    assert response_activate_owner.json()["detail"] == "Cannot activate an owner"
    
    # Clean up - delete created users
    user_collection.delete_one({"_id": expert_user["_id"]})
    user_collection.delete_one({"_id": owner_user["_id"]})

def test_user_creation_and_activation():
    created_users = []
    deactivated_users = []

    # Step 1: Create 10 random users
    for _ in range(10):
        user_data = generate_random_user()
        url_register = "http://localhost:8000/register/"
        response = httpx.post(url_register, params=user_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        created_users.append(user_data["user_name"])

    # Step 2: Verify user creation by logging in
    for user_name in created_users:
        url_login = "http://localhost:8000/login/"
        response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
        assert response.status_code == 200
        assert response.json()["success"] is True

    # Step 3: Deactivate 5 users
    for user_name in created_users[:5]:
        url_activate_user = "http://localhost:8000/activate_user/"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        user = user_collection.find_one({"user_name": user_name})
        user_id = str(user["_id"])
        response = httpx.put(url_activate_user, params={"user_id": user_id, "activated": False}, headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
        deactivated_users.append(user_name)

    # Step 4: Verify deactivation
    for user_name in created_users[:5]:
        url_login = "http://localhost:8000/login/"
        response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
        assert response.status_code == 403
    for user_name in created_users[5:]:
        url_login = "http://localhost:8000/login/"
        response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
        assert response.status_code == 200
        assert response.json()["success"] is True        
    # Step 5: Clean up - delete created users
    for user_name in created_users:
        user_collection.delete_one({"user_name": user_name})


if __name__ == "__main__":
    pytest.main()
    # pytest.main(['-v', '--html=report.html'])