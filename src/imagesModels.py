from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, validator

class ImageInput(BaseModel):
    Image_Path: str
    PeriodOfDiseaesId: str
    Classification: list
    Confidence: list
    bbox: list
    Image_Class: int
    Resized_Path: str
    Annotated_Path: str