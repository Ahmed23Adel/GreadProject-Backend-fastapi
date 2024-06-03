from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.savedTreatmentModels import (
    TreatmentCreateResponse,
    TreatmentScheduleCreateResponse,
    TreatmentSchedulesRequest,
    SavedTreatmentScheduleRequest,
    SavedTreatmentScheduleResponse,
    SavedTreatmentScheduleItemResponse
)
from typing import List

@v1.get("/get_saved_treatment_schedule/", response_model=SavedTreatmentScheduleResponse)
async def get_saved_treatment_schedule(disease_name: str, token: str = Depends(get_token_auth_header_expert)):
    # Check if the disease name is valid
    if disease_name not in ["Early blight", "Late blight"]:
        raise HTTPException(status_code=400, detail="Disease name must be either 'Early blight' or 'Late blight'")

    # Query the disease collection for the document with the given disease name
    disease_document = disease_collection.find_one({"diseaseName": disease_name})

    if not disease_document:
        raise HTTPException(status_code=404, detail=f"No disease found with name '{disease_name}'")

    # Retrieve the defaultSavedTreatmentId from the disease document
    default_saved_treatment_id = disease_document.get("defaultSavedTreatment")
    # Query the SavedTreatmentSchedule collection for the document with the defaultSavedTreatment
    saved_treatment_schedule_document = saved_treatment_schedule_collection.find_one({"_id": default_saved_treatment_id})

    if not saved_treatment_schedule_document:
        raise HTTPException(status_code=404, detail="No Saved Treatment Schedule found for the given disease")

    # Retrieve the treatmentName from the SavedTreatmentSchedule document
    treatment_name = saved_treatment_schedule_document.get("treatmentName")
    treatment_desc = saved_treatment_schedule_document.get("treatmentDescription")
    # Query the SavedTreatmentScheduleItems collection for items with the defaultSavedTreatment
    print("default_saved_treatment_id", default_saved_treatment_id)
    saved_treatment_schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": default_saved_treatment_id})

    # Construct the list of treatment items
    treatment_items = []
    for item in saved_treatment_schedule_items:
        treatment_item = {
            "dayNumber": item["dayNumber"],
            "dayTreatment": item["dayTreatment"]
        }
        treatment_items.append(treatment_item)

    return {
        "success": True,
        "data": {
            "treatmentName": treatment_name,
            "treatmentDesc": treatment_desc,
            "treatmentItems": treatment_items
        }
    }   
    
    
    

@v1.post("/create_saved_treatment_schedule/", response_model=SavedTreatmentScheduleResponse)
async def create_saved_treatment_schedule(schedule_data: SavedTreatmentScheduleRequest, token: str = Depends(get_token_auth_header_expert)):
    # Insert the SavedTreatmentSchedule into the database
    saved_schedule_data = {
        "treatmentName": schedule_data.treatmentName,
        "description": schedule_data.description
    }
    treatment_id = saved_treatment_schedule_collection.insert_one(saved_schedule_data).inserted_id
    
    # Insert the SavedTreatmentScheduleItems into the database
    created_items = []
    for item_data in schedule_data.scheduleItems:
        new_item = {
            "treatmentId": treatment_id,
            "dayNumber": item_data.dayNumber,
            "dayTreatment": item_data.dayTreatment
        }
        item_id = saved_treatment_schedule_itmes_collection.insert_one(new_item).inserted_id
        created_items.append({
            "treatment_schedule_item_id": str(item_id),
            **new_item
        })

    return {
        "success": True,
        "data": { }
    }
    
    
    
@v1.get("/list_saved_treatments/")
async def list_saved_treatments(token: str = Depends(get_token_auth_header)):
    output_saved_treatments = []
    all_saved_treatments = list(saved_treatment_schedule_collection.find({}))

    for saved_treatment in all_saved_treatments:
        treatment_id = saved_treatment["_id"]
        treatment_items_cursor = saved_treatment_schedule_itmes_collection.find({"treatmentId": treatment_id})

        treatment_items = [
            {
                "dayNumber": item["dayNumber"],
                "dayTreatment": item["dayTreatment"]
            }
            for item in treatment_items_cursor
        ]

        output_saved_treatments.append({
            "treatmentName": saved_treatment["treatmentName"],
            "_id": str(treatment_id),
            "treatment_items": treatment_items
        })

    return {"success": True, "data": {"saved_treatments": output_saved_treatments}}

from bson import ObjectId

@v1.put("/update_default_saved_treatment/")
async def update_default_saved_treatment(disease_name: str, new_default_saved_treatment: str, token: str = Depends(get_token_auth_header_expert)):
    # Validate the disease name
    if disease_name not in ["Early blight", "Late blight"]:
        raise HTTPException(status_code=400, detail="Invalid disease name")

    # Convert disease name to lowercase for case-insensitive comparison
    disease_name_lower = disease_name.lower()

    # Query the Disease collection to find documents with the specified disease name
    disease_document = disease_collection.find_one({"diseaseName": {"$regex": f"^{disease_name_lower}$", "$options": "i"}})
    print("disease_document", disease_document)
    # Check if the document was found
    if not disease_document:
        raise HTTPException(status_code=404, detail=f"No disease found with the name: {disease_name}")

    # Validate new_default_saved_treatment as ObjectId
    try:
        new_default_saved_treatment_obj = ObjectId(new_default_saved_treatment)
    except:
        raise HTTPException(status_code=400, detail="Invalid new_default_saved_treatment")

    # Update the defaultSavedTreatment field in the matched document with the new value
    update_result = disease_collection.update_one(
        {"diseaseName": {"$regex": f"^{disease_name_lower}$", "$options": "i"}},
        {"$set": {"defaultSavedTreatment": new_default_saved_treatment_obj}}
    )

    return {"success": True, "data": {}}
