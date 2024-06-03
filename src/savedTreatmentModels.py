from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional
from datetime import date
from pydantic import BaseModel
from typing import List

class TreatmentCreateResponse(BaseModel):
    success: bool
    data: dict

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    
                }
            }
        }


class TreatmentScheduleCreateData(BaseModel):
    treatment_schedule_id: str
    treatmentId: str
    treatmentDate: str
    treatmentDesc: str
    treatmentDone: bool
    treatmentDoneBy: str

class TreatmentScheduleCreateResponse(BaseModel):
    success: bool
    data: dict

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": [
                  
                ]
            }
        }



class TreatmentScheduleItem(BaseModel):
    treatmentDate: str
    treatmentDesc: str

class TreatmentSchedulesRequest(BaseModel):
    treatmentId: str
    treatments: List[TreatmentScheduleItem]


################################################################
class SavedTreatmentScheduleItem(BaseModel):
    dayNumber: int
    dayTreatment: str

class SavedTreatmentScheduleRequest(BaseModel):
    treatmentName: str
    description: str
    scheduleItems: List[SavedTreatmentScheduleItem]

class SavedTreatmentScheduleItemResponse(BaseModel):
    treatment_schedule_item_id: str
    treatmentId: str
    dayNumber: str
    dayTreatment: str
    
## Response
class SavedTreatmentScheduleResponse(BaseModel):
    success: bool
    data: dict

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {}
            }
        }
        
        
class SavedTreatmentScheduleItemResponse(BaseModel):
    treatmentId: str
    dayNumber: str
    treatmentName: str
