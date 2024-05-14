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

def connect_to_db():
    global client, db, images_collection, treatment_collection, reports_collection, user_collection
    if client is None:
        import certifi
        ca = certifi.where()
        client = MongoClient(MONGO_CLIENT, tlsCAFile=ca)
        db = client[DB_NAME]
        images_collection = db['images']  
        treatment_collection = db['treatment']  
        reports_collection = db['reports']  
        user_collection = db["users"]

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
        # Check expiration time
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")