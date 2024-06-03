from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from src.basic import * 
from src.treatmentScheduleModels import (
    TreatmentScheduleResponse
)

@v1.get("/get-treatment-schedule")
async def get_treatment_schedule(
    period_of_treatment_id: str,
    token: str = Depends(get_token_auth_header)
):
    try:
        # Fetch treatment schedules for the given period_of_treatment_id
        treatment_schedules = treatment_schedule_collection.find({"periodOfTreatment": period_of_treatment_id})
        if not treatment_schedules:
            raise HTTPException(status_code=404, detail="Treatment schedules not found")
        
        response_data = []
        for schedule in treatment_schedules:
            date_scheduled = schedule.get("treatmentDate")
            treatment_done = schedule.get("treatmentDone")
            farmer_finished = ""

            # If treatment is done, get the user details
            if treatment_done:
                treatment_done_by = schedule.get("treatmentDoneBy")
                if treatment_done_by:
                    print("treatment_done_by", treatment_done_by)
                    user = user_collection.find_one({"_id": ObjectId(treatment_done_by)})
                    print("user", user)
                    if user:
                        farmer_finished = f"{user.get('firstname', '')} {user.get('lastname', '')}"

            response_data.append({
                "Date_Scheduled": date_scheduled,
                "Done": treatment_done,
                "Farmer_Finished": farmer_finished
            })

        return {"success": True, "data": {"schedule": response_data}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
