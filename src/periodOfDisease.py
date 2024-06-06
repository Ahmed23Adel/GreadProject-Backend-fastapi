from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.periodOfDiseaseModels import(
    PeriodOfDiseaseImage,
    RescheduleOption
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
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # If no open period, create a new one
        new_period_of_disease_image = {
            "zoneId": ObjectId(period_of_disease_image.zoneId),
            "dateCreated": today_start,
            "currentDisease": period_of_disease_image.currentDisease,
        }

        result = period_of_disease_collection.insert_one(new_period_of_disease_image)
        new_id = str(result.inserted_id)

        return {"success": True, "data": {"id": new_id}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@v1.put("/end_period_of_disease/", response_model=dict)
async def end_period_of_disease(
    period_of_disease_id: str,
    ender_expert_id: str,
    token: str = Depends(get_token_auth_header_expert)
):
    try:
        # Check if the period of disease exists, is open, and approved
        open_period_of_disease = period_of_disease_collection.find_one({
            "_id": ObjectId(period_of_disease_id),
            "$or": [
                {"enderExpertId": {"$exists": False}},
                {"enderExpertId": ""},
                {"dateEnded": {"$exists": False}},
                {"dateEnded": None}
            ],
            "approverExpertId": {"$ne": ""},
            "dateApprovedByExpert": {"$exists": True}
        })

        if not open_period_of_disease:
            raise HTTPException(status_code=400, detail="The period of disease is not open, approved, or does not exist")

        # Set dateEnded to today's end date and enderExpertId
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        update_result = period_of_disease_collection.update_one(
            {"_id": ObjectId(period_of_disease_id)},
            {"$set": {"dateEnded": today_end, "enderExpertId": ender_expert_id}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update the period of disease")

        # Update the treatment schedule items for the given period
        treatment_update_result = treatment_schedule_collection.update_many(
            {"periodOfTreatment": period_of_disease_id},
            {"$set": {"treatmentDone": True}}
        )

        return {"success": True, "data": {"updated_treatment_items": treatment_update_result.modified_count}}
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
  
@v1.put("/reschedule-zone-check", response_model=dict)
async def reschedule_zone_check(
    period_of_disease_id: str,
    expert_id: str,
    reschedule_option: RescheduleOption = RescheduleOption.DELETE_EXISTING,  # Default to delete existing items
    token: str = Depends(get_token_auth_header)
):
    try:
        # Fetch the period of disease document
        period_of_disease = period_of_disease_collection.find_one({
            "_id": ObjectId(period_of_disease_id),
            "approverExpertId": {"$ne": ""},
            "dateApprovedByExpert": {"$exists": True}
        })
        
        if not period_of_disease:
            raise HTTPException(status_code=400, detail="The period of disease is not open or does not exist")

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
        
        # Determine treatment schedule items based on specific or default treatment
        if specific_treatment_id:
            treatment_schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": ObjectId(specific_treatment_id)})
        else:
            current_disease = period_of_disease.get("currentDisease")
            if not current_disease:
                raise HTTPException(status_code=404, detail="Current disease not found in period of disease")
            
            disease = disease_collection.find_one({"diseaseName": current_disease})
            if not disease or "defaultSavedTreatment" not in disease:
                raise HTTPException(status_code=404, detail="Default treatment not found for the disease")
            
            default_treatment_id = disease["defaultSavedTreatment"]
            treatment_schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": default_treatment_id})

        # Handle rescheduling option
        if reschedule_option == RescheduleOption.DELETE_EXISTING:
            # Delete existing treatment schedule items
            treatment_schedule_collection.delete_many({"periodOfTreatment": period_of_disease_id})
        elif reschedule_option == RescheduleOption.KEEP_EXISTING:
            # Keep existing treatment schedule items
            pass

        # Create new entries in TreatmentSchedule for each day in the treatment schedule
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
            treatment_schedule_collection.insert_one(new_treatment_schedule)

        return {"success": True, "message": "Zone checked and treatment schedule created successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
