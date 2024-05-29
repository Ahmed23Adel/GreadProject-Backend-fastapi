from src.basic import *
from datetime import datetime
from fastapi import status, HTTPException, Depends
from datetime import date, datetime
from fastapi import Query
import numpy as np
from src.stasModels import (
    DatePics, 
    DatePicsModel,
    LocationHistory,
    LocationHistoryList,
    LocationHistoryModel,
    DatePerDiseasedPlantsResponse,
    DatePerDiseasedPlants,
    LocationsResponse,
    DataResponseLocations,
    DataResponseStatistics,
    DiseasesResponse,
    NewImage
)

from src.utils import (
    parse_date_from,
    parse_date_to,
    transform
)



@app.post("/images/create/")
def create_new_image(new_image: NewImage, token: str = Depends(get_token_auth_header)):
    # Convert Classification and Confidence lists to BSON-compatible format
    classification_bson = [int(x) for x in new_image.Classification]
    confidence_bson = [float(x) for x in new_image.Confidence]

    # Create the new image document
    new_image_doc = {
        "Image_Path": new_image.Image_Path,
        "Location": new_image.Location,
        "Date": new_image.Date,
        "Time": new_image.Time,
        "Classification": classification_bson,
        "Confidence": confidence_bson,
        "bbox": new_image.bbox,
        "Image_Class": new_image.Image_Class,
        "Edited": new_image.Edited,
        "Treated": new_image.Treated,
        "Resized_Path": new_image.Resized_Path,
        "Annotated_Path": new_image.Annotated_Path
    }

    # Insert the new image document into the database
    result = images_collection.insert_one(new_image_doc)

    if result.inserted_id:
        return {"success": True, "message": "Image created successfully", "image_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create image")

def get_pics_stats_at_date(specific_date):
    # Count images with Image_Class 0 or 1
    total_images = images_collection.count_documents({"Date": specific_date})
    count_diseased = images_collection.count_documents({"Date": specific_date, "Image_Class": {"$in": [0, 1]}})
    count_diseased_edited = images_collection.count_documents({
        "Date": specific_date,
        "Image_Class": {"$in": [0, 1]},
        "Edited": 1
    })
    count_diseased_EB = images_collection.count_documents({"Date": specific_date, "Image_Class": {"$in": [0]}})
    count_diseased_LB = images_collection.count_documents({"Date": specific_date, "Image_Class": {"$in": [1]}})
    
    if total_images != 0:
        # Calculate percentages
        percentage_diseased = (count_diseased / total_images) * 100
        percentage_edited = (count_diseased_edited / total_images) * 100
        mod_percentage = (count_diseased_edited / count_diseased) * 100 if count_diseased != 0 else 0
        percentage_diseased_EB = (count_diseased_EB / total_images) * 100
        percentage_diseased_LB = (count_diseased_LB / total_images) * 100
    else:
        percentage_diseased = 0
        percentage_edited = 0
        mod_percentage = 0
        percentage_diseased_EB = 0
        percentage_diseased_LB = 0
    # Create TodayPics instance
    date_str = datetime.strftime(specific_date, "%d-%m-%Y")
    latest_pics = DatePics(
        latest_date=date_str,
        count=total_images,
        percentage_diseased=f"{percentage_diseased:.2f}",
        percentage_diseased_after_mod=f"{percentage_edited:.2f}",
        mod_rate=f"{mod_percentage:.2f}",
        EB_per= percentage_diseased_EB,
        LB_per = percentage_diseased_LB
    )

    return DatePicsModel(success=True, data=latest_pics)

@app.get("/latest_pics", status_code=status.HTTP_200_OK, response_model=DatePicsModel)
def get_latest_pics(token: str = Depends(get_token_auth_header)):
    # Find the latest date in the images collection
    latest_entry = images_collection.find_one(sort=[("Date", -1)])
    print("latest_entry", latest_entry)
    if not latest_entry:
        raise HTTPException(status_code=404, detail="No images found")
    latest_date_str = latest_entry["Date"]
    # latest_date = datetime.strptime(latest_date_str, "%d-%m-%Y")
    # formatted_latest_date = latest_date.strftime("%d-%m-%Y")
    return get_pics_stats_at_date(latest_date_str)
    

def parse_date(date_str: str = Query(...)) -> date:
    try:
        parsed_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please provide the date in MM/DD/YYYY format."
        )
    return parsed_date

@app.get("/date_pics", status_code=status.HTTP_200_OK, response_model=DatePicsModel)
def get_date_pics(token: str = Depends(get_token_auth_header), query_date: date = Depends(parse_date)):
    query_date = query_date.strftime("%d-%m-%Y")
    query_date_obj = datetime.strptime(query_date, "%d-%m-%Y")
    formatted_date_str = query_date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    formatted_date_obj = datetime.strptime(formatted_date_str, "%Y-%m-%dT%H:%M:%S.%f+00:00")
    print("formatted_date_obj", type(formatted_date_obj), formatted_date_obj)
    return get_pics_stats_at_date(formatted_date_obj)


@app.get("/disease_mons_percentage")
def get_disease_mons_percentage(token: str = Depends(get_token_auth_header),):
    # Define the months
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    EB_data = [0] * len(months)
    LB_data = [0] * len(months)

    # Query MongoDB collection
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    end_of_year = datetime(current_year, 12, 31)

    cursor = images_collection.find({
        "Date": {
            "$gte": start_of_year,
            "$lte": end_of_year
        }
    })

    # Process data to calculate monthly percentage
    for document in cursor:
        date = document["Date"]
        month_index = date.month
        if document["Image_Class"] == 0:
            EB_data[month_index] += 1
        elif document["Image_Class"] == 1:
            LB_data[month_index] += 1

    # Calculate percentages
    total_images_per_month = [EB + LB for EB, LB in zip(EB_data, LB_data)]
    print("total_images_per_month", total_images_per_month)
    print("EB_data", EB_data)
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

    try:
        # Convert dates to datetime objects
        start_datetime = datetime.strptime(from_date.strftime("%d-%m-%Y"), "%d-%m-%Y") if from_date.year > 1 else datetime.min
        end_datetime = datetime.strptime(to_date.strftime("%d-%m-%Y"), "%d-%m-%Y") if to_date.year > 1 else datetime.max
        print("start_datetimelll", start_datetime, end_datetime)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use %d-%m-%Y.")
    # Query MongoDB for documents within the date range and specific location
    images = images_collection.find({
        "Date": {
            "$gte": start_datetime,
            "$lte": end_datetime
        },
        "Location": location
    })
    # print("imagesssss", [im['Date'] for im in images])
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
    print("unique_dates", unique_dates)
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
        "dates": [datetime.strftime(date, "%d-%m-%Y") for date in unique_dates],
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

    # try:
        fields_to_get = {
            "Image_Path": 1,
            "Location": 1,
            "Date": 1,
            "Image_Class": 1,
            "Confidence": 1,
            "_id": 1  
        }
        date_obj = datetime.strptime(date, "%d-%m-%Y")
        start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        print("Start date:", start_date)

        # Calculate the end date by adding one day
        end_date = start_date + timedelta(days=1)
        print("End date:", end_date)
        # start_datetimelll 1990-03-01 00:00:00 2024-06-01 00:00:00
        # Query to retrieve images by date range
        
        images_count = images_collection.count_documents({
            "Date": {
                "$gte": start_date,
                "$lte": end_date
            },           
            }
        )

        EB_count = images_collection.count_documents({
            "Date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "Image_Class": 0
            
            }
        )
        LB_count = images_collection.count_documents({
            "Date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "Image_Class": 1
            
            }
        )
        

        print("images")
        print(images_count)
        print(EB_count)
        print(LB_count)
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
    # except:
    #     raise HTTPException(status_code=500, detail="Failed to create this statistics")




