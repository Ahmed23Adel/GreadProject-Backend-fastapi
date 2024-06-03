from src.basic import *
from datetime import datetime
from fastapi import status, HTTPException, Depends
from datetime import date, datetime
from fastapi import Query
import numpy as np
from datetime import datetime, timedelta


@v1.get("/get-todays-treatments", status_code=status.HTTP_200_OK)
def get_todays_treatments(token: str = Depends(get_token_auth_header_farmer)):
    try:
        # Get today's date in the required format
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)

        # Find documents in treatment_schedule_collection where treatmentDate is today and treatmentDone is false
        today_entries_cursor = treatment_schedule_collection.find({
            "treatmentDate": {"$gte": today_start, "$lt": tomorrow_start},
            "treatmentDone": False
        })

        today_entries = list(today_entries_cursor)  # Convert cursor to list to print and iterate over it

        results = []

        for entry in today_entries:
            period_of_treatment_id = entry.get("periodOfTreatment")
            id = str(entry.get("_id"))

            if period_of_treatment_id:
                # Fetch the corresponding period of treatment document
                period_of_treatment_doc = period_of_disease_collection.find_one({"_id": ObjectId(period_of_treatment_id)})

                if period_of_treatment_doc:
                    zone_id = period_of_treatment_doc.get("zoneId")
                    if zone_id:
                        # Fetch the corresponding zone document
                        zone_doc = zones_collection.find_one({"_id": zone_id})

                        if zone_doc:
                            zone_name = zone_doc.get("zoneName")
                            treatment = zone_doc.get("specificTreatmentId", "")

                            if not treatment:
                                # If Specific_Treatment is not available, get the Current_Disease
                                current_disease = zone_doc.get("currentDisease", "")
                                if current_disease:
                                    # Fetch the treatment from treatment_collection using Current_Disease
                                    treatment_doc = treatment_collection.find_one({"Disease": current_disease})
                                    treatment = treatment_doc.get("Treatment", "")
                            print("entry", entry)
                            # Append the result
                            results.append({
                                "id": id,
                                "Zone_Name": zone_name,
                                "Treatment": entry["treatmentDesc"]
                            })

        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from bson.objectid import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument

@v1.put("/update_scheduling_done", status_code=status.HTTP_200_OK)
def update_scheduling_done(scheduling_id: str, user_id: str, token: str = Depends(get_token_auth_header_farmer)):
    try:
        # Convert the scheduling_id to ObjectId
        scheduling_object_id = ObjectId(scheduling_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid scheduling ID format")

    try:
        # Convert the user_id to ObjectId
        user_object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Find the document by its ID and update the Done field to True and treatmentDoneBy to user_id
    scheduling_document = treatment_schedule_collection.find_one_and_update(
        {"_id": scheduling_object_id},
        {"$set": {"treatmentDone": True, "treatmentDoneBy": str(user_object_id)}},
        return_document=ReturnDocument.AFTER
    )

    if not scheduling_document:
        raise HTTPException(status_code=404, detail="Scheduling document not found")

    return {"success": True, "message": "Scheduling updated successfully"}



