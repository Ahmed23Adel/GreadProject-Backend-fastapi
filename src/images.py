
from src.basic import *
from datetime import datetime
from fastapi import status, HTTPException, Depends
from datetime import date, datetime
from fastapi import Query
import numpy as np

from src.stasModels import (
    LocationHistory,
    LocationHistoryList,
    LocationHistoryModel,

)

from src.utils import (
    parse_date_from,
    parse_date_to,
    transform
)
@v1.get("/location-history", status_code=status.HTTP_200_OK, response_model=LocationHistoryModel)
def get_location_history(
    token: str = Depends(get_token_auth_header),
    period_of_disease_id: str = Query(...),
):
    # Query MongoDB for documents with the specific PeriodOfDiseaseId
    print("period_of_disease_id", period_of_disease_id)
    images = images_collection.find({"PeriodOfDiseaesId": period_of_disease_id})
    # Convert ObjectId to string and return the documents
    result = []
    for image in images:
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

        # Calculate mean confidence percentage
        confidences = image.get("Confidence", [])
        mean_confidence = np.mean(confidences) if confidences else 0

        # Construct item data
        date_str = datetime.strftime(image.get("Date", ""), "%d-%m-%Y")
        item_data = {
            "itemImageSrc": transform(image.get("Image_Path", "")),
            "thumbnailImageSrc": transform(image.get("Resized_Path", "")),
            "alt": f"{mean_confidence:.2f}%",
            "title": date_str,
        }
        result.append(item_data)
    print("Results", result)
    # Return the response using LocationHistoryModel
    all_locs = [LocationHistory(**item) for item in result]
    all_locs_lst = LocationHistoryList(allHistory=all_locs)
    return LocationHistoryModel(success=True, data=all_locs_lst)
