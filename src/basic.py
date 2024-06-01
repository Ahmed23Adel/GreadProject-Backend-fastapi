from dotenv import load_dotenv
import os
from pymongo import MongoClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, Header, HTTPException
from datetime import date
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt 
from datetime import datetime, timedelta
from jwt import PyJWTError
from bson import ObjectId

load_dotenv() 
MONGO_CLIENT = os.environ.get('MONGO_CLIENT') 
DB_NAME = os.environ.get('DB_NAME')
SECRET_KEY = os.environ.get('SECRET_KEY') 
ALGORITHM = "HS256"

print("Keys")
print("MONGO_CLIENT: ", MONGO_CLIENT)
print("DB_NAME: ", DB_NAME)
print("SECRET_KEY: ", SECRET_KEY)

client = None
db = None
images_collection = None
treatment_collection = None
reports_collection = None
user_collection = None
location_collection = None
zonesTreatmentScheduling_collection = None

def connect_to_db():
    global client, db, images_collection, treatment_collection, reports_collection, user_collection, location_collection, zonesTreatmentScheduling_collection
    if client is None:
        import certifi
        ca = certifi.where()
        client = MongoClient(MONGO_CLIENT, tlsCAFile=ca)
        db = client[DB_NAME]
        images_collection = db['images']  
        treatment_collection = db['treatment']  
        reports_collection = db['reports']  
        user_collection = db["users"]
        location_collection = db['location']
        zonesTreatmentScheduling_collection = db["zonesTreatmentScheduling"]

connect_to_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow credentials (e.g., cookies or Authorization headers)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

print("Done building basics")

security = HTTPBearer()


def is_user_activated(user_collection, user_id: str) -> bool:
    user_id_obj = ObjectId(user_id)
    user = user_collection.find_one({"_id": user_id_obj})
    print("user_id", user_id)
    print("user: ",user)
    if user:
        print(user.get("activated", False))
        return user.get("activated", False)
    else:
        return False
    
def get_token_auth_header_parent(expected_user_type: str):
    if expected_user_type == "expert":
        return get_token_auth_header_expert
    elif expected_user_type == "owner":
        return get_token_auth_header_owner


def get_token_auth_header(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
        user_id = payload["user_id"]
        print("get_token_auth_header user_id", user_id)
        if not is_user_activated(user_collection ,user_id):
            raise HTTPException(
                status_code=401,
                detail="User is not activated"
            )
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_token_auth_header_expert(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_type = payload["user_type"]
        if user_type != "expert":
            raise HTTPException(status_code=401, detail="Only expert can perform this operation")
        user_id = payload["user_id"]
        print("user_id", user_id)
        if not is_user_activated(user_collection ,user_id):
            raise HTTPException(
                status_code=401,
                detail="User is not activated"
            )
        # Check expiration time
        
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    

def get_token_auth_header_farmer(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_type = payload["user_type"]
        if user_type != "farmer":
            raise HTTPException(status_code=401, detail="Only farmers can perform this operation")
        user_id = payload["user_id"]
        if not is_user_activated(user_collection ,user_id):
            raise HTTPException(
                status_code=401,
                detail="User is not activated"
            )
        # Check expiration time
        
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def get_token_auth_header_owner(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_type = payload["user_type"]
        if user_type != "owner":
            raise HTTPException(status_code=401, detail="Only owner can perform this operation")
        user_id = payload["user_id"]

        # Check if the user is activated
        # Assuming you have a function `is_user_activated` to check if the user is activated
        if not is_user_activated(user_collection ,user_id):
            raise HTTPException(
                status_code=401,
                detail="User is not activated"
            )
        # Check expiration time
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")