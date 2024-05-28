from src.basic import *
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
import jwt  
import bcrypt
from bson import ObjectId


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.post("/register/")
async def register(user_name: str, password: str, type: str):
    existing_user = user_collection.find_one({"user_name": user_name})

    if existing_user:
        return {"success": False, "data": {"user_id": None}}

    # Hash the password before saving
    hashed_password = hash_password(password)

    # Insert the new user into the database
    new_user = {
        "user_name": user_name,
        "password": hashed_password,
        "type": type.lower(),
        "activated": True  # Adding the activated field with default value True
    }
    user_id = user_collection.insert_one(new_user).inserted_id

    return {"success": True, "data": {"user_id": str(user_id)}}



@app.get("/users/")  
async def get_all_users(token: str = Depends(get_token_auth_header_owner)):
    users = list(user_collection.find({}, {"password": 0}))  # Exclude the password field
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
    existing_user = user_collection.find_one({"user_name": user_name})

    if existing_user and verify_password(password, existing_user["password"]):
        if not existing_user.get("activated", False):
            raise HTTPException(status_code=403, detail="User is not activated")
        
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        user_type = existing_user.get("type")
        access_token = create_access_token(
            data={"sub": user_name, 'user_type': user_type}, expires_delta=access_token_expires
        )
        return {
            "success": True,
            "data": {
                "user_type": user_type,
                "user_id": str(existing_user.get("_id")),
                "token": access_token,
            },
        }
    else:
        raise HTTPException(status_code=401, detail="Incorrect password or username")

@app.put("/activate_user/")
async def activate_user(user_id: str, activated: bool, token: str = Depends(get_token_auth_header_owner)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    existing_user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if existing_user.get("type") == "owner":
        raise HTTPException(status_code=403, detail="Cannot activate an owner")

    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"activated": activated}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "data": {"user_id": user_id, "activated": activated}}


@app.put("/reset_password/")
def reset_password(username: str, new_password: str, token: str = Depends(get_token_auth_header_owner)):
    existing_user = user_collection.find_one({"user_name": username})
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the new password before updating
    hashed_password = hash_password(new_password)

    # Update the user's password in the database
    result = user_collection.update_one(
        {"_id": existing_user["_id"]},
        {"$set": {"password": hashed_password}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "message": "Password reset successfully"}