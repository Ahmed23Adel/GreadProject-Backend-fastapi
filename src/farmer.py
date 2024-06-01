from src.basic import *
from datetime import datetime
from fastapi import status, HTTPException, Depends
from datetime import date, datetime
from fastapi import Query
import numpy as np


@app.get("/get-todays-treatments", status_code=status.HTTP_200_OK)
def get_todays_treatments(token: str = Depends(get_token_auth_header_farmer)):
    # Get today's date in the required format
    # Get zones look in locatoins collection if not then check default in treatmetn 
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    print("today_start", today_start)  # Debug print
    print("tomorrow_start", tomorrow_start)  # Debug print

    # Find documents in zonesTreatmentScheduling_collection where Date_Scheduled is today and Done is false
    today_entries_cursor = zonesTreatmentScheduling_collection.find({
        "Date_Scheduled": {"$gte": today_start, "$lt": tomorrow_start},
        "Done": False
    })
    
    today_entries = list(today_entries_cursor)  # Convert cursor to list to print and iterate over it
    print("today_entries", today_entries)  # Debug print to check the entries
    
    results = []

    for entry in today_entries:
        zone_name = entry["Zone_Name"]
        id = entry["_id"]
        print("zone_name", zone_name)
        # Fetch the corresponding location document
        # Locatoin might have a specfic treatment for this locatoin 
        location_doc = location_collection.find_one({"Zone_Name": zone_name})

        if location_doc:
            treatment = location_doc.get("Specific_Treatment", "")
            print("treatment", treatment)
            if not treatment:
                # If Specific_Treatment is not available, get the Current_Disease
                # Locatoin does have treatment, so go just take current disease and search in treatment collection
                current_disease = location_doc.get("Current_Disease", "")
                if current_disease:
                    # Fetch the treatment from treatment_collection using Current_Disease
                    treatment_doc = treatment_collection.find_one({"Disease": current_disease})
                    treatment = treatment_doc.get("Treatment", "") if treatment_doc else ""

            # Append the result
            results.append({
                "id": id,
                "Zone_Name": zone_name,
                "Treatment": treatment
            })

    return {"success": True, "data": results}

from bson.objectid import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

@app.put("/update_scheduling_done", status_code=status.HTTP_200_OK)
def update_scheduling_done(scheduling_id: str, token: str = Depends(get_token_auth_header_farmer)):
    try:
        # Convert the scheduling_id to ObjectId
        scheduling_object_id = ObjectId(scheduling_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid scheduling ID format")
    print("scheduling_object_id", scheduling_object_id)
    # Find the document by its ID and update the Done field to True
    scheduling_document = zonesTreatmentScheduling_collection.find_one_and_update(
        {"_id": str(scheduling_object_id)},
        {"$set": {"Done": True}},
        return_document=ReturnDocument.AFTER
    )

    if not scheduling_document:
        raise HTTPException(status_code=404, detail="Scheduling document not found")

    return {"success": True, "message": "Scheduling updated successfully"}


