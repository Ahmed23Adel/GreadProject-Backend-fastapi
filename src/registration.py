from src.basic import *
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
import jwt  
import bcrypt
from bson import ObjectId
from datetime import datetime, timezone
from src.registrationModels import (
    RegisterResponse,
    LoginResponse,
    ActivateUserResponse
)
 
print("Intializing Registration endpoints...")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_input_length(input_str: str, field_name: str, min_length = 5, max_length = 12):
    if not (min_length <= len(input_str) <= max_length):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be between {min_length} and {max_length} characters")

@v1.post("/register/", response_model=RegisterResponse)
async def register(firstname: str, lastname: str,
                   user_name: str, password: str,
                   creator_owner_id: str, 
                   type: str, token: str = Depends(get_token_auth_header_owner)):
    # Validate input lengths
    validate_input_length(user_name, "username")
    validate_input_length(password, "password")
    validate_input_length(firstname, "first name", min_length=0, max_length=12)
    validate_input_length(lastname, "last name", min_length=0, max_length=12)

    if not type.lower() in ['expert', 'owner', 'farmer']:
        raise HTTPException(status_code=400, detail="Type must be one of the following values (expert, owner, farmer)")
    print("username", user_name)
    existing_user = user_collection.find_one({"user_name": user_name})
    print("existing_user", existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    date_created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    # Insert the new user into the database
    new_user = {
        "firstname": firstname,
        "lastname": lastname,
        "user_name": user_name,
        "password": hash_password(password),
        "date_created": date_created,
        "creator_owner_id": creator_owner_id,
        "type": type.lower(),
        "activated": True  # Adding the activated field with default value True
    }
    user_id = user_collection.insert_one(new_user).inserted_id

    return {"success": True, "data": {"user_id": str(user_id)}}



def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    print("data", data.get("user_id") )
    to_encode.update({
        "exp": expire.timestamp(),
        "user_type": data.get("user_type"),  
        "user_id": str(data.get("user_id"))
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")  
    return encoded_jwt



@v1.get("/login/")
async def login(user_name: str, password: str, response_mode= LoginResponse):
    # Check if user exists in the database
    existing_user = user_collection.find_one({"user_name": user_name})

    if existing_user and verify_password(password, existing_user["password"]):
        if not existing_user.get("activated", False):
            raise HTTPException(status_code=403, detail="User is not activated")
        
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        user_type = existing_user.get("type")
        user_id = existing_user.get("_id")
        access_token = create_access_token(
            data={"sub": user_name, 'user_type': user_type, 'user_id': user_id}, expires_delta=access_token_expires
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

@v1.put("/activate_user/", response_model= ActivateUserResponse)
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


@v1.put("/reset_password/")
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