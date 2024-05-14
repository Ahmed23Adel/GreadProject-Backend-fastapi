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
MONGO_CLIENT = os.getenv("MONGO_CLIENT")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

client = None
db = None
images_collection = None
treatment_collection = None
reports_collection = None
user_collection = None

def connect_to_db():
    global client, db, images_collection, treatment_collection, reports_collection, user_collection
    if client is None:
        client = MongoClient(MONGO_CLIENT)
        db = client[DB_NAME]
        images_collection = db['images']  
        treatment_collection = db['treatment']  
        reports_collection = db['reports']  
        user_collection = db["users"]

connect_to_db()

app = FastAPI()
origins = ["http://localhost:5173"]  # Add any other origins you want to allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins
    allow_credentials=True,  # Allow credentials (e.g., cookies or Authorization headers)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

print("Done building basics")

def get_token_auth_header(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check expiration time
        if datetime.now() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
        return token
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")