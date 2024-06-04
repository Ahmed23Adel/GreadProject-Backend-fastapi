from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.savedTreatmentModels import (
    SavedTreatmentScheduleRequest,
    SavedTreatmentScheduleResponse,
)
from typing import List
@v1.get("/get_all_treatments_and_schedules/")
def get_all_treatments_and_schedules(token: str = Depends(get_token_auth_header)):
    """
     Retrieves all treatment schedules and their associated treatment items.

    Raises:
        HTTPException: 401 Unauthorized if token is invalid.
    """

    # Get all saved treatment schedule documents
    all_schedules = saved_treatment_schedule_collection.find({})

    # Check if there are any schedules
    if not all_schedules:
        return {"success": False, "detail": "No treatment schedules found"}

    # List to store all treatment data
    treatments = []

    # Loop through each schedule document
    for schedule in all_schedules:
        treatment_name = schedule.get("treatmentName")
        treatment_desc = schedule.get("treatmentDescription")
        schedule_id = schedule["_id"]

        # Find all schedule items for the current treatment
        schedule_items = saved_treatment_schedule_itmes_collection.find({"treatmentId": schedule_id})

        # List to store treatment items for the current schedule
        treatment_items = []

        # Loop through each schedule item and add to the list
        for item in schedule_items:
            treatment_item = {
                "dayNumber": item["dayNumber"],
                "dayTreatment": item["dayTreatment"],
            }
            treatment_items.append(treatment_item)

        # Add treatment data with its items to the treatments list
        treatments.append({
            "treatmentName": treatment_name,
            "treatmentDescription": treatment_desc,
            "treatmentItems": treatment_items,
        })
        print("treatments", treatments)
    return {"success": True, "data": {"saved_treatments" : treatments}}

@v1.get("/get_saved_treatment_schedule/", response_model=SavedTreatmentScheduleResponse)
async def get_saved_treatment_schedule(disease_name: str, token: str = Depends(get_token_auth_header)):
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
    """The create_saved_treatment_schedule endpoint is designed to create a new saved treatment 
        schedule along with its associated treatment schedule items. 
        
    """
    existing_treatment = saved_treatment_schedule_collection.find_one({"treatmentName": schedule_data.treatmentName})
    if existing_treatment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A treatment schedule with the same name already exists."
        )
        
    saved_schedule_data = {
        "treatmentName": schedule_data.treatmentName,
        "description": schedule_data.treatmentDescription
    }
    treatment_id = saved_treatment_schedule_collection.insert_one(saved_schedule_data).inserted_id
    
    # Insert the SavedTreatmentScheduleItems into the database
    created_items = []
    for item_data in schedule_data.treatmentItems:
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
    
@v1.put("/update_saved_treatment_schedule/{treatmentName}", response_model=SavedTreatmentScheduleResponse)
async def update_saved_treatment_schedule(
    treatmentName: str,
    schedule_data: SavedTreatmentScheduleRequest,
    token: str = Depends(get_token_auth_header_expert)
):
    """The update_saved_treatment_schedule endpoint updates an existing saved treatment 
        schedule identified by its ID. 
        
    """
    
    # Find the existing treatment schedule
    existing_treatment = saved_treatment_schedule_collection.find_one({"treatmentName": treatmentName})

    if not existing_treatment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment schedule with the provided treatmentName does not exist."
        )

    # Extract treatment ID from the found document
    treatment_id = str(existing_treatment["_id"])  # Assuming 
    # Update the treatment schedule data
    saved_treatment_schedule_collection.update_one(
        {"_id": ObjectId(treatment_id)},
        {"$set": {"treatmentName": schedule_data.treatmentName, "treatmentDescription": schedule_data.treatmentDescription}}
    )

    # Get existing schedule item IDs
    existing_item_ids = [str(item["_id"]) for item in saved_treatment_schedule_itmes_collection.find({"treatmentId": ObjectId(treatment_id)})]

    # Update existing items and track deleted ones
    items_to_update = []
    deleted_items = set(existing_item_ids)
    for item_data in schedule_data.treatmentItems:
        item_id = str(item_data.dayNumber)  # Use dayNumber as a unique identifier (modify if needed)
        if item_id in existing_item_ids:
            deleted_items.remove(item_id)
            items_to_update.append({
                "_id": ObjectId(item_id),
                "dayTreatment": item_data.dayTreatment
            })
        else:
            # New item
            new_item = {
                "treatmentId": ObjectId(treatment_id),
                "dayNumber": item_data.dayNumber,
                "dayTreatment": item_data.dayTreatment
            }
            saved_treatment_schedule_itmes_collection.insert_one(new_item)

    # Delete items marked for deletion
    if deleted_items:
        delete_filter = {"_id": {"$in": [ObjectId(item_id) for item_id in deleted_items]}}
        saved_treatment_schedule_itmes_collection.delete_many(delete_filter)

    # Update existing items
    if items_to_update:
        saved_treatment_schedule_itmes_collection.update_many({"_id": {"$in": [item["_id"] for item in items_to_update]}}, {"$set": {"dayTreatment": "$dayTreatment"}})  # Update only dayTreatment

    return {
        "success": True,
        "data": { }  # You can add updated treatment details here
    }
    
    
@v1.delete("/delete_saved_treatment_schedule/{treatmentName}", response_model=SavedTreatmentScheduleResponse)
async def delete_saved_treatment_schedule(
    treatmentName: str,
    token: str = Depends(get_token_auth_header_expert)
):
    """
    The delete_saved_treatment_schedule endpoint deletes an existing saved treatment 
    schedule along with all its associated treatment schedule items.
    """
    
    # Find the existing treatment schedule
    existing_treatment = saved_treatment_schedule_collection.find_one({"treatmentName": treatmentName})
    if not existing_treatment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment schedule with the provided treatmentName does not exist."
        )

    # Extract treatment ID from the found document
    treatment_id = existing_treatment["_id"]
    
    # Delete the treatment schedule
    saved_treatment_schedule_collection.delete_one({"_id": treatment_id})
    
    # Delete associated treatment schedule items
    saved_treatment_schedule_itmes_collection.delete_many({"treatmentId": treatment_id})
    
    return {
        "success": True,
        "data": {}
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
