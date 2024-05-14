from dotenv import load_dotenv
import os
from pymongo import MongoClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, Header, HTTPException
from datetime import date
from typing import Optional

load_dotenv() 
MONGO_CLIENT = os.getenv("MONGO_CLIENT")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")

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

def get_token_auth_header(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token not provided. Please include a bearer token in the request header.")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token. Please provide a valid bearer token.")
    token = parts[1]
    # Here you can add your logic to check if the token is valid
    # For simplicity, let's assume the token is valid for now
    return token