from basic import *
from datetime import datetime, timedelta
import jwt
from fastapi import status, HTTPException, Depends
from pydantic import BaseModel

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



from datetime import datetime, timedelta
import jwt  # Import jwt module from PyJWT

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")  # Assuming you're using HMAC algorithm
    return encoded_jwt



async def get_current_user(token: str = Depends(create_access_token)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@app.get("/login/")
async def login(user_name: str, password: str):
    # Check if user exists in the database
    existing_user = user_collection.find_one({"user_name": user_name, "password": password})

    if existing_user:
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(
            data={"sub": user_name}, expires_delta=access_token_expires
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
