from src.basic import *
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
import jwt  


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 

@app.post("/register/")
async def register(user_name: str, password: str, type:str):
    existing_user = user_collection.find_one({"user_name": user_name})

    if existing_user:
        return {"success": False, "data": {"user_id": 'None'}}

    # Insert the new user into the database
    new_user = {
        "user_name": user_name,
        "password": password,
        "type": type.lower()  # You can set the default type for new users
    }
    user_id = user_collection.insert_one(new_user).inserted_id

    return {"success": True, "data": {"user_id": 'user_id'}}



@app.get("/users/")  
async def get_all_users():
    users = list(user_collection.find({}))
    if not users:
        return {"success":False, "data": {"users": []}}
    
    for user in users:
        user["_id"] = str(user["_id"])
    
    return {"success": True, "data": {"users": users}}


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    print("data", data.get("user_type") )
    to_encode.update({
        "exp": expire.timestamp(),
        "user_type": data.get("user_type")  
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")  
    return encoded_jwt



    


@app.get("/login/")
async def login(user_name: str, password: str):
    # Check if user exists in the database
    existing_user = user_collection.find_one({"user_name": user_name, "password": password})

    if existing_user:
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        user_type = existing_user.get("type")
        access_token = create_access_token(
            data={"sub": user_name, 'user_type': user_type}, expires_delta=access_token_expires
        )
        return {
            "success": True,
            "data": {
                "user_type": existing_user.get("type"),
                "user_id": str(existing_user.get("_id")),
                "token": access_token,
            },
        }
    else:
        return {"success": False, "data": {"user_type": ""}}
