from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.treatmentModels import (
    TreatmentCreateResponse,
    TreatmentScheduleCreateResponse,
    TreatmentSchedulesRequest,
    SavedTreatmentScheduleRequest,
    SavedTreatmentScheduleResponse
)
from typing import List


@v1.post("/create_treatment/", response_model=TreatmentCreateResponse,)
async def create_treatment(treatment_desc: str, token: str = Depends(get_token_auth_header_expert)):
    # Insert the new treatment into the database
    new_treatment = {
        "treatmentDescription": treatment_desc
    }
    treatment_collection.insert_one(new_treatment).inserted_id
    
    return {
        "success": True,
        "data": {}
    }
    

@v1.post("/create_treatment_schedule/", response_model=TreatmentScheduleCreateResponse)
async def create_treatment_schedule(treatment_schedules: TreatmentSchedulesRequest, token: str = Depends(get_token_auth_header_expert)):
    created_objects = []
    treatment_id = treatment_schedules.treatmentId
    treatments = treatment_schedules.treatments
    for schedule_data in treatments:
        new_schedule = {
            "treatmentId": treatment_id,
            "treatmentDate": schedule_data.treatmentDate,
            "treatmentDesc": schedule_data.treatmentDesc,
            "treatmentDone": False,
            "treatmentDoneBy": None  # Initially set to null
        }
        schedule_id = treatment_schedule_collection.insert_one(new_schedule).inserted_id
        created_objects.append({
            "treatment_schedule_id": str(schedule_id),
            **new_schedule
        })

    return {
        "success": True,
        "data": {}
    }
    
    
    
    