from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from pydantic import BaseModel
from typing import List


################################################################
class SavedTreatmentScheduleItemRequest(BaseModel):
    dayNumber: int
    dayTreatment: str = Field(..., min_length=3, max_length=200)

class SavedTreatmentScheduleRequest(BaseModel):
    treatmentName: str = Field(..., min_length=3, max_length=200)
    treatmentDescription: str = Field(..., min_length=3, max_length=200)
    treatmentItems: List[SavedTreatmentScheduleItemRequest]
    
    @validator('treatmentItems')
    def check_treatment_items_length(cls, v):
        if len(v) < 1:
            raise ValueError('There must be at least one schedule item')
        return v

class SavedTreatmentScheduleResponse(BaseModel):
    success: bool
    data: dict