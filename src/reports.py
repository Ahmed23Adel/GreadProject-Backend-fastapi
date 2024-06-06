from src.basic import *
from fastapi import FastAPI
from fastapi import status, HTTPException, Depends
import secrets
from fastapi.security import OAuth2PasswordBearer
import os
from fastapi import FastAPI, Depends, HTTPException, status, Query,Body
from pydantic import BaseModel
from datetime import date, datetime
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId


@v1.get('/get_all_reports')
def get_all_reports():
    reports = list(reports_collection.find({},{'_id':0}))
    
    # Convert MongoDB documents to Report objects
    print(reports)
    
    return {'data':reports}


class Com(BaseModel):
    id:str
    order: int
    title: str
    imagePath: str
    paragraph: str
    
    
class SuccessResponse(BaseModel):
    success: bool = True
    
class QuestionAnswer(BaseModel):
    question_order:int
    question_answer:str
class Report(BaseModel):
    expert_id:str
    components:list[Com]
    created_at:str
    questions_answers:list[QuestionAnswer]
    
@v1.post("/add_report", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def add_report(report: Report):
    user_id = report.expert_id
    expert_name = user_collection.find_one({"_id":ObjectId(user_id)}, {"firstname": 1, "lastname": 1})
    print("expert_name", expert_name)
    all_name = expert_name["firstname"] + " " + expert_name["lastname"]
    print("expert_name", expert_name)
    # Convert the report object to a dictionary
    report_dict = report.model_dump()
    report_dict["expert_id"] = all_name
    # Insert the report into the database
    result = reports_collection.insert_one(report_dict)
    
    # Check if the insertion was successful
    if result.inserted_id:
        print(result.inserted_id)
        return SuccessResponse(date=result.inserted_id)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add report")