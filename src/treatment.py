from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.treatmentModels import (
    SuccessResponse,
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
    return {"success": True, "message": f"Disease name: {diseaesName}, Default treatment for {diseaesName} updated to: {treatment}"}



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


@app.get("/get-diseased-locations", status_code=status.HTTP_200_OK)
def get_diseased_locations(token: str = Depends(get_token_auth_header)):
    # Your update logic here
    #diseaesName =  EB LB
    unique_locations = list(images_collection.distinct("Location", {"$and": [{"Image_Class": {"$in": [0, 1]}}, {"Location": {"$exists": True}}]}))

    return {"success": True, "data": {"locations": unique_locations}}

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
        {"$set": {"Treated": 1, "Image_Class": 3}},  # Update to set the "treated" attribute to 1
    )
    # Your logic to declare the location healthy here
    return SuccessResponse(success=True)