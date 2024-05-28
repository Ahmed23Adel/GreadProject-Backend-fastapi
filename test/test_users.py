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


# def generate_random_user(user_type = "expert"):
#     user_name = str(uuid.uuid4())
#     password = "testpassword"
#     return {"user_name": user_name, "password": password, "type": user_type}

# def test_activate_only_experts():
#     # Step 1: Create an "expert" user and an "owner" user
#     expert_user_data = generate_random_user("expert")
#     owner_user_data = generate_random_user("owner")
    
#     response_expert = httpx.post("http://localhost:8000/register/", params=expert_user_data)
#     assert response_expert.status_code == 200
#     assert response_expert.json()["success"] is True
    
#     response_owner = httpx.post("http://localhost:8000/register/", params=owner_user_data)
#     assert response_owner.status_code == 200
#     assert response_owner.json()["success"] is True
    
#     expert_user = user_collection.find_one({"user_name": expert_user_data["user_name"]})
#     owner_user = user_collection.find_one({"user_name": owner_user_data["user_name"]})
    
#     expert_user_id = str(expert_user["_id"])
#     owner_user_id = str(owner_user["_id"])
    
#     # Step 2: Attempt to activate both users
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#     response_activate_expert = httpx.put(
#         "http://localhost:8000/activate_user/", 
#         params={"user_id": expert_user_id, "activated": True},
#         headers=headers
#     )
#     response_activate_owner = httpx.put(
#         "http://localhost:8000/activate_user/", 
#         params={"user_id": owner_user_id, "activated": True},
#         headers=headers
#     )
    
#     # Step 3: Verify activation results
#     assert response_activate_expert.status_code == 200
#     assert response_activate_expert.json()["success"] is True
#     assert response_activate_expert.json()["data"]["activated"] is True
    
#     assert response_activate_owner.status_code == 403
#     assert response_activate_owner.json()["detail"] == "Cannot activate an owner"
    
#     # Clean up - delete created users
#     user_collection.delete_one({"_id": expert_user["_id"]})
#     user_collection.delete_one({"_id": owner_user["_id"]})

# def test_user_creation_and_activation():
#     created_users = []
#     deactivated_users = []

#     # Step 1: Create 10 random users
#     for _ in range(10):
#         user_data = generate_random_user()
#         url_register = "http://localhost:8000/register/"
#         response = httpx.post(url_register, params=user_data)
#         assert response.status_code == 200
#         assert response.json()["success"] is True
#         created_users.append(user_data["user_name"])

#     # Step 2: Verify user creation by logging in
#     for user_name in created_users:
#         url_login = "http://localhost:8000/login/"
#         response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
#         assert response.status_code == 200
#         assert response.json()["success"] is True

#     # Step 3: Deactivate 5 users
#     for user_name in created_users[:5]:
#         url_activate_user = "http://localhost:8000/activate_user/"
#         headers = {
#             "Authorization": f"Bearer {token}"
#         }
#         user = user_collection.find_one({"user_name": user_name})
#         user_id = str(user["_id"])
#         response = httpx.put(url_activate_user, params={"user_id": user_id, "activated": False}, headers=headers)
#         assert response.status_code == 200
#         assert response.json()["success"] is True
#         deactivated_users.append(user_name)

#     # Step 4: Verify deactivation
#     for user_name in created_users[:5]:
#         url_login = "http://localhost:8000/login/"
#         response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
#         assert response.status_code == 403
#     for user_name in created_users[5:]:
#         url_login = "http://localhost:8000/login/"
#         response = httpx.get(url_login, params={"user_name": user_name, "password": "testpassword"})
#         assert response.status_code == 200
#         assert response.json()["success"] is True        
#     # Step 5: Clean up - delete created users
#     for user_name in created_users:
#         user_collection.delete_one({"user_name": user_name})


# def test_register_username_password_length():
#     # Test with a username less than or equal to 5 characters
#     response = httpx.post("http://localhost:8000/register/", params={"user_name": "shrt", "password": "longenough", "type": "expert"})
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Username must be more than 5 characters"
    
#     # Test with a password less than or equal to 5 characters
#     response = httpx.post("http://localhost:8000/register/", params={"user_name": "validusername", "password": "shrt", "type": "expert"})
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Password must be more than 5 characters"




# url_register = "http://localhost:8000/register/"
# url_delete_user = "http://localhost:8000/delete_user/"
# owner_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZCIsInVzZXJfdHlwZSI6Im93bmVyIiwiZXhwIjoxNzE3MDE0MTMxLjg1NDM4N30.NBSdCfUqiuzJyFtStF9wzQQiEG8WgWGraJd1PVegNGw"
# expert_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1lZDEiLCJ1c2VyX3R5cGUiOiJleHBlcnQiLCJleHAiOjE3MTcwMTQwNzcuNzc4NjE3fQ.WlN0EuWOpX4NUseltJdaryEA53twFIVwPBGFPWA-Z-4"

# def delete_user_from_db(user_name):
#     result = user_collection.delete_one({"user_name": user_name})
#     assert result.deleted_count == 1

# def test_register_no_token():
#     """
#     Test the registration endpoint without an authentication token.
    
#     Objective: Ensure the registration fails with a 403 status code and the 'Not authenticated' detail.
#     """
#     response_no_token = httpx.post(url_register, params={"user_name": "noTokenUser", "password": "validpassword", "type": "expert"})
#     assert response_no_token.status_code == 403  # Assuming 403 Forbidden for missing token
#     assert response_no_token.json()["detail"] == "Not authenticated"

# def test_register_with_expert_token():
#     """
#     Test the registration endpoint with an expert token.
    
#     Objective: Ensure the registration fails with a 401 status code.
#     """
#     headers_expert = {
#         "Authorization": f"Bearer {expert_token}"
#     }
#     response_expert_token = httpx.post(url_register, params={"user_name": "expertUser", "password": "validpassword", "type": "expert"}, headers=headers_expert)
#     assert response_expert_token.status_code == 401  # Assuming 401 Unauthorized for non-owner token


# def test_register_with_owner_token():
#     """
#     Test the registration endpoint with an owner token.
    
#     Objective: Ensure the registration succeeds with a 200 status code and the 'success' field is True.
#     """
#     headers_owner = {
#         "Authorization": f"Bearer {owner_token}"
#     }
#     response_owner_token = httpx.post(url_register, params={"user_name": "ownerUser", "password": "validpassword", "type": "expert"}, headers=headers_owner)
#     assert response_owner_token.status_code == 200
#     assert response_owner_token.json()["success"] is True

#     # Clean up: delete the created user
#     delete_user_from_db("ownerUser")

# # Run the test function
# if __name__ == "__main__":
#     pytest.main(["-v", "--html=report.html", "--self-contained-html"])

if __name__ == "__main__":
    pytest.main()
    # pytest.main(['-v', '--html=report.html'])