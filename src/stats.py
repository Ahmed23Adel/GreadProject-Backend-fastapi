from src.basic import *
from datetime import datetime
from fastapi import status, HTTPException, Depends
from datetime import date, datetime
from fastapi import Query
import numpy as np
from src.stasModels import (
    TodayPics, 
    TodayPicsModel,
    DatePics, 
    DatePicsModel,
    LocationHistory,
    LocationHistoryList,
    LocationHistoryModel,
    DatePerDiseasedPlantsResponse,
    DatePerDiseasedPlants,
    LocationsResponse,
    DataResponseLocations,
    DataResponseStatistics
)

from src.utils import (
    parse_date_from,
    parse_date_to,
    transform
)



@app.get("/today_pics", status_code=status.HTTP_200_OK, response_model=TodayPicsModel)
def get_today_pics(token: str = Depends(get_token_auth_header)):
    # Get the current date
    current_date = date.today().strftime("%Y-%m-%d")

    # Count images with Image_Class 0 or 1
    total_images = images_collection.count_documents({"Date": current_date})
    count_diseased = images_collection.count_documents({"Date": current_date, "Image_Class": {"$in": [0, 1]}})
    count_diseased_edited = images_collection.count_documents({
        "Date": current_date,
        "Image_Class": {"$in": [0, 1]},
        "Edited": 1
    })
    if total_images != 0:
        # Calculate percentages
        percentage_diseased = (count_diseased / total_images) * 100
        percentage_edited = (count_diseased_edited / total_images) * 100
        mod_percentage = count_diseased_edited*100/count_diseased
    else:
        percentage_diseased = 0
        percentage_edited = 0
        mod_percentage = 0
        
    # Create TodayPics instance
    today_pics = TodayPics(
        count=total_images,
        percentage_diseased=percentage_diseased,
        percentage_diseased_after_mod=percentage_edited,
        mod_rate=mod_percentage
    )
    return TodayPicsModel(success=True, data=today_pics)


def parse_date(date_str: str = Query(...)) -> date:
    try:
        parsed_date = datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please provide the date in MM/DD/YYYY format."
        )
    return parsed_date

@app.get("/date_pics", status_code=status.HTTP_200_OK, response_model=DatePicsModel)
def get_date_pics(token: str = Depends(get_token_auth_header), query_date: date = Depends(parse_date)):
    query_date = query_date.strftime("%Y-%m-%d")
    total_images = images_collection.count_documents({"Date": query_date})
    count_diseased = images_collection.count_documents({"Date": query_date, "Image_Class": {"$in": [0, 1]}})
    count_diseased_EB = images_collection.count_documents({"Date": query_date, "Image_Class": {"$in": [0]}})
    count_diseased_LB = images_collection.count_documents({"Date": query_date, "Image_Class": {"$in": [1]}})
    count_diseased_edited = images_collection.count_documents({
        "Date": query_date,
        "Image_Class": {"$in": [0, 1]},
        "Edited": 1
    })
    if total_images != 0:
        # Calculate percentages
        percentage_diseased = (count_diseased / total_images) * 100
        percentage_diseased_EB = (count_diseased_EB / total_images) * 100
        percentage_diseased_LB = (count_diseased_LB / total_images) * 100
        percentage_edited = (count_diseased_edited / total_images) * 100
        mod_percentage = count_diseased_edited*100/count_diseased
        
    else:
        percentage_diseased = 0
        percentage_diseased_EB = 0
        percentage_diseased_LB = 0
        percentage_edited = 0
        mod_percentage = 0
        
    date_pics = DatePics(
        count=total_images,
        percentage_diseased=percentage_diseased,
        percentage_diseased_after_mod=percentage_edited,
        mod_rate=mod_percentage,
        EB_per = percentage_diseased_EB,
        LB_per = percentage_diseased_LB,
    )
    return DatePicsModel(success=True, data=date_pics)


@app.get("/disease_mons_percentage")
def get_disease_mons_percentage(token: str = Depends(get_token_auth_header),):
    # Define the months
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    EB_data = [0] * len(months)
    LB_data = [0] * len(months)

    # Query MongoDB collection
    cursor = images_collection.find({})

    # Process data to calculate monthly percentage
    for document in cursor:
        date_string = document["Date"]
        month_index = int(date_string.split("-")[1]) - 1
        if document["Image_Class"] == 0:
            EB_data[month_index] += 1
        elif document["Image_Class"] == 1:
            LB_data[month_index] += 1

    # Calculate percentages
    total_images_per_month = [EB + LB for EB, LB in zip(EB_data, LB_data)]
    EB_percentage = [round((EB / total) * 100, 2) if total > 0 else 0 for EB, total in zip(EB_data, total_images_per_month)]
    LB_percentage = [round((LB / total) * 100, 2) if total > 0 else 0 for LB, total in zip(LB_data, total_images_per_month)]

    # Return the response
    data = {
        "mons": months,
        "EB": EB_percentage,
        "LB": LB_percentage
    }
    
    # Return the response using the defined Pydantic model
    # return DiseaseMonsPercentageModel(success=True, data=data)
    return {"success": True, "data": data}

@app.get("/location-history", status_code=status.HTTP_200_OK, response_model=LocationHistoryModel)
def get_location_history(
    token: str = Depends(get_token_auth_header),
    location: str = Query(...),
    from_date: date = Depends(parse_date_from),
    to_date: date = Depends(parse_date_to),
):
    # if from_date and to_date are 01/01/0001 then it should return the whole history
    # Define static data for the response
    try:
        start_datetime = from_date.strftime("%Y-%m-%d")
        end_datetime =  to_date.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    print(start_datetime)
    print(end_datetime)
    # Query MongoDB for documents within the date range and specific location
    images = images_collection.find({
        "Date": {
            "$gte": start_datetime,
            "$lte": end_datetime
        },
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

        # Calculate mean confidence percentage
        confidences = image.get("Confidence", [])
        mean_confidence = np.mean(confidences) if confidences else 0

        # Construct item data
        item_data = {
            "itemImageSrc": transform(image.get("Image_Path", "")),
            "thumbnailImageSrc": transform(image.get("Resized_Path", "")),
            "alt": f"{mean_confidence:.2f}%",
            "title": image.get("Date", ""),
            "treatment": treatment
        }
        result.append(item_data)

    # Return the response using LocationHistoryModel
    all_locs = [LocationHistory(**item) for item in result]
    all_locs_lst = LocationHistoryList(allHistory=all_locs)
    return LocationHistoryModel(success=True, data=all_locs_lst)


@app.get("/get-date-per-diseased-plants", status_code=status.HTTP_200_OK, response_model=DatePerDiseasedPlantsResponse)
def get_date_per_diseased_plants(token: str = Depends(get_token_auth_header), location: str = Query(...)):
    unique_dates = list(images_collection.distinct("Date", {"Location": location}))
    percentages = []
    for date in unique_dates:
        # Count total number of images for this date and location
        total_images = images_collection.count_documents({"Location": location, "Date": date})
        
        # Count number of diseased images (Image_Class 0 or 1) for this date and location
        diseased_images = images_collection.count_documents({"Location": location, "Date": date, "Image_Class": {"$in": [0, 1]}})
        
        # Store results for this date
        percentages.append(diseased_images*100/total_images)
    # Static data (sample data)
    static_data = {
        "dates": unique_dates,
        "percentages": percentages
    }

    # Return the static data wrapped in the response model
    return DatePerDiseasedPlantsResponse(success=True, data=DatePerDiseasedPlants(**static_data))


@app.get("/get_all_locations", status_code=status.HTTP_200_OK, response_model=DataResponseLocations)
def get_all_locations(token: str = Depends(get_token_auth_header)):
    # Sample list of locations
    unique_locations = list(images_collection.distinct("Location"))


    # Return the response
    return DataResponseLocations(success=True, data=LocationsResponse(locations=unique_locations))


@app.get("/get_disease_statistics", status_code=status.HTTP_200_OK, response_model=DataResponseStatistics)
def get_disease_statistics(token: str = Depends(get_token_auth_header), date: str = Query(...)):
    # Sample data for diseases and percentages (replace with your actual data retrieval logic)

    try:
        fields_to_get = {
            "Image_Path": 1,
            "Location": 1,
            "Date": 1,
            "Image_Class": 1,
            "Confidence": 1,
            "_id": 1  
        }
        input_date = datetime.strptime(date, "%d/%m/%Y").date()

        # Format the date into Year-Month-Day format
        date_filter = input_date.strftime("%Y-%m-%d")
        print(date_filter)
        # Query to retrieve images by date
        images = list(images_collection.find({"Date": str(date_filter)},fields_to_get))
        images_EB = list(images_collection.find({"Date": str(date_filter), "Image_Class": 0}, fields_to_get))
        images_LB = list(images_collection.find({"Date": str(date_filter), "Image_Class": 1}, fields_to_get))

        
        images_count = len(images)
        EB_count = len(images_EB)
        LB_count = len(images_LB)
        if images_count != 0 :
            EB_percentage = EB_count*100/images_count
            LB_percentage = LB_count*100/images_count
        else:
            EB_percentage = 0
            LB_percentage = 0
            
        diseases = ["Early blight", "Late blight"]

        percentages =[int(EB_percentage),int(LB_percentage)]
       
        # Return the response
        return DataResponseStatistics(success=True, data=DiseasesResponse(diseases=diseases, percentages=percentages))
    except:
        return DataResponseStatistics(success=False)




