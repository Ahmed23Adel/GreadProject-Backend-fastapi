from fastapi import FastAPI
import secrets
from fastapi.security import OAuth2PasswordBearer
import os
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
import numpy as np
from basic import *




# regApp = app
from registration import *
from stats import *
from treatment import *