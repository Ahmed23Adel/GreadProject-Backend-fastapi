from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

class TreatmentScheduleResponse(BaseModel):
    date_scheduled: datetime
    Done: bool
    Farmer_Finished: str