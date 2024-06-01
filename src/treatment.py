from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.treatmentModels import (
    SuccessResponse,
    UpdateTreatmentRequest
)


@app.get("/get-default-treatment", status_code=status.HTTP_200_OK)
def get_default_treatment(token: str = Depends(get_token_auth_header)):
    # Your update logic here
    #diseaesName =  EB LB
    text = []
    treatments = list(treatment_collection.find())
    op = {}
    for treatment in treatments:
        disease = treatment.get("Disease", "")
        default_treatment = treatment.get("Treatment", "")
        if disease:
            op[disease] = default_treatment
        
    return {"success": True, "data": op}



@app.put("/update-default-treatment", status_code=status.HTTP_200_OK)
def update_default_treatment(diseaesName: str, treatment: str, token: str = Depends(get_token_auth_header_expert)):
    # Your update logic here
    #diseaesName =  EB LB
    result = treatment_collection.update_many(
        {"Disease": diseaesName},  # Filter criteria
        {"$set": {"Treatment": treatment}}  # Update to set the "treated" attribute to 1
    )
    print(treatment)
    return {"success": True, "data": f"Disease name: {diseaesName}, Default treatment for {diseaesName} updated to: {treatment}"}



@app.post("/accept-location-treated", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def accept_location_treated(location_name: str, token: str = Depends(get_token_auth_header_expert)):
    result = images_collection.update_many(
        {"Location": location_name},  # Filter criteria
        {"$set": {"Treated": 1}}  # Update to set the "treated" attribute to 1
    )
    # Your logic to process the location name here
    return SuccessResponse()


@app.put("/accept-treated", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def accept_treated(location: str = Query(...), token: str = Depends(get_token_auth_header_expert)):
    # Your logic to process the location here
    result = images_collection.update_many(
        {"Location": location},  # Filter criteria
        {"$set": {"Treated": 1}}  # Update to set the "treated" attribute to 1
    )
    return SuccessResponse()


# @app.get("/get-diseased-locations", status_code=status.HTTP_200_OK)
# def get_diseased_locations(token: str = Depends(get_token_auth_header)):
#     # Your update logic here
#     #diseaesName =  EB LB
#     # TODO maake sure substituting image_class with treated is ok
#     unique_locations = list(images_collection.distinct("Location", {"$and": [{"Treated": {"$in": [0]}}, {"Location": {"$exists": True}}]}))

#     return {"success": True, "data": {"locations": unique_locations}}

@app.get("/get-diseased-locations", status_code=status.HTTP_200_OK)
def get_diseased_locations(token: str = Depends(get_token_auth_header)):
    # once the zone  gets diseased again it should make  Checked_By_Expert = false again
    locations = list(location_collection.find({}, {"Zone_Name": 1, "Checked_By_Expert": 1, "_id": 0}))
    # return locations
    return {"success": True, "data": {"locations": locations}}

@app.get("/diseased-zones", status_code=status.HTTP_200_OK)
def get_diseased_zones(token: str = Depends(get_token_auth_header)):
    # Find all zones with Diseased=true
    diseased_zones = list(location_collection.find({"Diseased": True}))

    results = []

    for zone in diseased_zones:
        zone_name = zone["Zone_Name"]
        specific_treatment = zone.get("Specific_Treatment")
        current_disease = zone.get("Current_Disease")
        is_zone_checked_by_expert = zone.get("Checked_By_Expert")
        _id = zone.get("_id")
        # Determine the treatment to use
        if specific_treatment:
            treatment = specific_treatment
        else:
            # Look up the default treatment for the disease
            disease_info = treatment_collection.find_one({"Disease": current_disease})
            if disease_info:
                treatment = disease_info.get("Treatment")
            else:
                treatment = "No treatment available"

        results.append({
            "_id": _id,
            "Zone_Name": zone_name,
            "Treatment": treatment,
            "Checked_By_Expert": is_zone_checked_by_expert
        })

    return {"success": True, "data": {"locations": results}}

@app.post("/set-location-checked/", status_code=status.HTTP_200_OK)
def set_location_checked(location_name: str, token: str = Depends(get_token_auth_header_expert)):
    result = location_collection.update_one(
        {"Zone_Name": location_name},
        {"$set": {"Checked_By_Expert": True}}
    )

    # Return a success response
    return {"success": True, "message": f"Location '{location_name}' Checked_By_Expert set to True"}

@app.get("/get-all-locations", status_code=status.HTTP_200_OK)
def get_all_locations(token: str = Depends(get_token_auth_header)):
    # Your update logic here
    #diseaesName =  EB LB
    unique_locations = list(images_collection.distinct("Location"))
    return {"success": True, "data": {"locations": unique_locations}}


@app.put("/update_treatment", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def update_treatment(location: str, treatment: str, token: str = Depends(get_token_auth_header_expert)):
    # Your logic to update the treatment for the location here
    result = treatment_collection.update_one(
        {"Location": location},  # Filter criteria
        {"$set": {"treatment": treatment}},  # Update operation
        upsert=True  # If the document doesn't exist, insert it
    )
    # Check if the update was successful
    if result.modified_count > 0:
        # If the update was successful, return a success response
        return SuccessResponse()
    else:
        # Check if the document was inserted as new
        if result.upserted_id is not None:
            # Set days_treatment to 5 for the newly inserted document
            treatment_collection.update_one(
                {"_id": result.upserted_id},  # Filter by the inserted document's _id
                {"$set": {"days_treatment": 5}}  # Set days_treatment to 5
            )
        # If no documents were modified, it means no matching document was found for the specified location
        # Return a failure response indicating that the location was not found
        return {"success": True, "message": "Not updated"}

@app.get("/get_treatment_value", status_code=status.HTTP_200_OK)##
def get_treatment_value(location: str = Query(...), token: str = Depends(get_token_auth_header)):
    # Your logic to process the location here
    # if user hasn't specified the specific treatment return the default
    # treatment_document = treatment_collection.find_one({"Location": location},{"treatment":1})
    images = images_collection.find({
        "Location": location
    })

    # Convert ObjectId to string and return the documents
    result = []
    for image in images:
        image_id = str(image["_id"])
        location = image.get("Location")
        
        # First, try to get treatment by location
        if location:
            location_treatment = treatment_collection.find_one({"Location": location})
            treatment = location_treatment.get("treatment") if location_treatment else None
        else:
            treatment = None
        
        # If location treatment is empty or location is not specified, find treatment by Disease
        if not treatment:
            image_class = image.get("Image_Class")
            disease = "Early_Blight" if image_class == 0 else "Late_Blight"
            disease_treatment = treatment_collection.find_one({"Disease": disease})
            treatment = disease_treatment.get("Treatment") if disease_treatment else None

    return {"success": True, "data": {"treatment": treatment}}


@app.put("/extend_location_by_days", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def extend_location_by_days(location: str, period: str, token: str = Depends(get_token_auth_header_expert)):
    # Your logic to extend the location by the specified number of days here
    result = treatment_collection.update_one({"Location": location}, {"$set": {"days_treatment": period}})
    
    # Check if the update was successful
    if result.modified_count > 0:
        # If the update was successful, return a success response
        return SuccessResponse()
    else:
        # If no documents were modified, it means no matching document was found for the specified location
        # Return a failure response indicating that the location was not found
        return {"success": True, "message": "Not updated"}


@app.put("/declare_location_healthy", status_code=status.HTTP_200_OK, response_model=SuccessResponse)
def declare_location_healthy(location: str, token: str = Depends(get_token_auth_header_expert)):
    result = images_collection.update_many(
        {"Location": location},  # Filter criteria
        # TODO make sure "Image_Class": 3 is ok to be removed
        {"$set": {"Treated": 1, }},  # Update to set the "treated" attribute to 1
    )
    # Your logic to declare the location healthy here
    return SuccessResponse(success=True)

def declare_location_unhealthy(location: str):
    result = images_collection.update_many(
        {"Location": location},  # Filter criteria
        {"$set": {"Treated": 0}},  # Update to set the "treated" attribute to 1
    )
    # Your logic to declare the location healthy here
    return SuccessResponse(success=True)


def delete_treatment_by_location(location: str):
    # Find and delete the document with the specified location
    result = treatment_collection.delete_one({"Location": location})

    # Check if a document was deleted
    if result.deleted_count == 1:
        return {"success": True, "message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found for the specified location")
    



@app.post("/schedule-zones", status_code=status.HTTP_201_CREATED)
def schedule_zones(start_date: str, end_date: str, zone_name: str, token: str = Depends(get_token_auth_header_expert)):
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.strptime(end_date, "%d-%m-%Y")

    # Check if end date is greater than or equal to start date
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be greater than or equal to start date")

    # Iterate through each day between start_date and end_date
    current_date = start_date
    while current_date <= end_date:
        # Format the current_date in the required format for MongoDB
        formatted_date = current_date.strftime("%Y-%m-%dT00:00:00.000+00:00")
        
        # Create the document to be inserted into the collection
        schedule_data = {
            "Zone_Name": zone_name,
            "Date_Scheduled": formatted_date,
            "Done": False
        }

        # Insert the document into the collection
        zonesTreatmentScheduling_collection.insert_one(schedule_data)

        # Move to the next day
        current_date += timedelta(days=1)
        print("formatted_date", formatted_date)

    return {"success": True, "data": {}}



from pymongo import DESCENDING  # Import DESCENDING for sorting in descending order

@app.get("/zone-scheduled", status_code=status.HTTP_200_OK)
def check_scheduled(location: str, token: str = Depends(get_token_auth_header)):
    # Retrieve entries from the database
    entries = list(zonesTreatmentScheduling_collection.find(
        {"Zone_Name": location},
        {"Date_Scheduled": 1, "Done": 1, "Farmer_Finished": 1, "_id": 0}
    ).sort("Date_Scheduled", DESCENDING))  # Sort by Date_Scheduled in descending order

    # Format the entries
    formatted_entries = []
    for entry in entries:
        date_scheduled = datetime.strptime(str(entry["Date_Scheduled"]), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
        
        # Retrieve the username from the user collection based on the Farmer_Finished id
        farmer_finished_id = entry.get("Farmer_Finished", "")
        if farmer_finished_id:
            user_id_obj = ObjectId(farmer_finished_id)
            user = user_collection.find_one({"_id": user_id_obj}, {"user_name": 1})
            username = user.get("user_name", "") if user else ""
        else:
            username = ""
        
        formatted_entries.append({"Date_Scheduled": date_scheduled, "Done": entry["Done"], "Farmer_Finished": username})
    
    return {"success": True, "data": {"schedule": formatted_entries}}



@app.put("/update-specific-treatment", status_code=200)
def update_specific_treatment(zone_name: str, specific_treatment: str, token: str = Depends(get_token_auth_header)):
    try:
        # Find the document by zone_name
        location_document = location_collection.find_one({"Zone_Name": zone_name})
        if not location_document:
            raise HTTPException(status_code=404, detail="Zone not found")

        # Update the Specific_Treatment field
        location_collection.update_one(
            {"Zone_Name": zone_name},
            {"$set": {"Specific_Treatment": specific_treatment}}
        )

        return {"success": True, "data": {"message": "Specific Treatment updated successfully"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))