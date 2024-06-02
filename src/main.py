from fastapi import FastAPI
import secrets
from fastapi.security import OAuth2PasswordBearer
import os
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
import numpy as np
from src.basic import *



print("IN main")
# regApp = app
from src.registration import *
# from src.stats import *
# from src.treatment import *
# from src.farmer import *
from src.zones import *