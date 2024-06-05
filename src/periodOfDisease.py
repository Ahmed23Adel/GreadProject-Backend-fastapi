from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.periodOfDiseaseModels import(
    PeriodOfDiseaseImage,
)
from datetime import datetime, timedelta


@v1.post("/create_period_of_disease", response_model=dict)
async def create_period_of_disease(
    period_of_disease_image: PeriodOfDiseaseImage,
    token: str = Depends(get_token_auth_header)
):
    try:
        PeriodOfDiseaseImage.validate_zone_id(period_of_disease_image.zoneId)
        PeriodOfDiseaseImage.validate_current_disease(period_of_disease_image.currentDisease)

        # Check if there is any open period of disease for the given zoneId
        open_period_of_disease = period_of_disease_collection.find_one({
            "zoneId": ObjectId(period_of_disease_image.zoneId),
            "$or": [
                {"enderExpertId": {"$exists": False}},
                {"enderExpertId": ""},
                {"dateEnded": {"$exists": False}},
                {"dateEnded": None}
            ]
        })

        if open_period_of_disease:
            raise HTTPException(status_code=400, detail="There is already an open period of disease for the given zoneId")

        # If no open period, create a new one
        new_period_of_disease_image = {
            "zoneId": ObjectId(period_of_disease_image.zoneId),
            "dateCreated": period_of_disease_image.dateCreated,
            "dateApprovedByExpert": period_of_disease_image.dateApprovedByExpert,
            "approverExpertId": period_of_disease_image.approverExpertId,
            "dateEnded": period_of_disease_image.dateEnded,
            "enderExpertId": period_of_disease_image.enderExpertId,
            "currentDisease": period_of_disease_image.currentDisease,
            "specificTreatmentId": period_of_disease_image.specificTreatmentId,
        }

        result = period_of_disease_collection.insert_one(new_period_of_disease_image)
        new_id = str(result.inserted_id)

        return {"success": True, "data": {"id": new_id}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    
@v1.delete("/reject_period_of_disease", response_model=dict)
async def reject_period_of_disease(period_of_disease_id: str, token: str = Depends(get_token_auth_header_expert)):
    try:
        # Check if the period of disease exists and if it hasn't been approved by an expert
        existing_period_of_disease = period_of_disease_collection.find_one({"_id": ObjectId(period_of_disease_id)})
        if existing_period_of_disease is None:
            raise HTTPException(status_code=404, detail="Period of disease not found")

        if (
            existing_period_of_disease.get("approverExpertId") 
            and existing_period_of_disease["approverExpertId"] != ""
            or existing_period_of_disease.get("dateApprovedByExpert")
        ):
            raise HTTPException(status_code=400, detail="Cannot reject an approved period of disease")

        # Delete the period of disease
        period_of_disease_collection.delete_one({"_id": ObjectId(period_of_disease_id)})

        return {"success": True, "data": {}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    
    
from datetime import datetime

@v1.put("/set-zone-checked", response_model=dict)
async def set_zone_checked(
    period_of_disease_id: str,
    expert_id: str,
    token: str = Depends(get_token_auth_header)
):
    try:
        # Fetch the period of disease document
        period_of_disease = period_of_disease_collection.find_one({"_id": ObjectId(period_of_disease_id)})
        if not period_of_disease:
            raise HTTPException(status_code=404, detail="Period of disease not found")
        
        # Update the period of disease document
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        period_of_disease_collection.update_one(
            {"_id": ObjectId(period_of_disease_id)},
            {
                "$set": {
                    "dateApprovedByExpert": current_date,
                    "approverExpertId": expert_id
                }
            }
        )

        # Retrieve specificTreatmentId from the period of disease document
        specific_treatment_id = period_of_disease.get("specificTreatmentId")
        # print("specific_treatment_id,", specific_treatment_id)
        # If specificTreatmentId exists and is not empty, fetch the treatment schedule
        if specific_treatment_id:
            treatment_schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": ObjectId(specific_treatment_id)})
            # print("in if", specific_treatment_id, list(treatment_schedule_items))
        else:
            print("in else")
            # If specificTreatmentId is not present, fetch the currentDisease
            current_disease = period_of_disease.get("currentDisease")
            if not current_disease:
                raise HTTPException(status_code=404, detail="Current disease not found in period of disease")
            
            # Look up the default treatment in the disease collection
            disease = disease_collection.find_one({"diseaseName": current_disease})
            if not disease or "defaultSavedTreatment" not in disease:
                raise HTTPException(status_code=404, detail="Default treatment not found for the disease")
            
            default_treatment_id = disease["defaultSavedTreatment"]
            treatment_schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": default_treatment_id})

        # Create new entries in TreatmentSchedule for each day in the treatment schedule
        # print("treatment_schedule_items", list(treatment_schedule_items))
        for item in treatment_schedule_items:
            day_num = int(item["dayNumber"])
            treatment_date = current_date + timedelta(days=day_num)
            treatment_desc = item["dayTreatment"]

            new_treatment_schedule = {
                "periodOfTreatment": period_of_disease_id,
                "treatmentDate": treatment_date,
                "treatmentDesc": treatment_desc,
                "treatmentDone": False,
                "treatmentDoneBy": None
            }
            print("new_treatment_schedule", new_treatment_schedule)
            treatment_schedule_collection.insert_one(new_treatment_schedule)

        return {"success": True, "message": "Zone checked and treatment schedule created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@v1.put("/set-period-of-disease-specific-treatment", response_model=dict)
async def set_period_of_disease_specific_treatment(
    period_of_disease_id: str,
    treatment_id: str,
    token: str = Depends(get_token_auth_header_expert)):
    try:
        # Validate and convert the period_of_disease_id and treatment_id to ObjectId
        period_of_disease_id = ObjectId(period_of_disease_id)

        # Fetch the period of disease document
        period_of_disease = period_of_disease_collection.find_one({"_id": period_of_disease_id})
        if not period_of_disease:
            raise HTTPException(status_code=404, detail="Period of disease not found")

        # Update the period of disease document with the new specific treatment ID
        period_of_disease_collection.update_one(
            {"_id": period_of_disease_id},
            {
                "$set": {
                    "specificTreatmentId": treatment_id
                }
            }
        )

        return {"success": True, "message": "Specific treatment ID updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))