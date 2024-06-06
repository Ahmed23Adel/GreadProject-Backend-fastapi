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
from datetime import datetime, timedelta

from src.utils import (
    parse_date_from,
    parse_date_to,
    transform
)


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

@v1.get("/latest_pics", status_code=status.HTTP_200_OK, response_model=DatePicsModel)
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

@v1.get("/date_pics", status_code=status.HTTP_200_OK, response_model=DatePicsModel)
def get_date_pics(token: str = Depends(get_token_auth_header), query_date: date = Depends(parse_date)):
    query_date = query_date.strftime("%d-%m-%Y")
    query_date_obj = datetime.strptime(query_date, "%d-%m-%Y")
    formatted_date_str = query_date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    formatted_date_obj = datetime.strptime(formatted_date_str, "%Y-%m-%dT%H:%M:%S.%f+00:00")
    print("formatted_date_obj", type(formatted_date_obj), formatted_date_obj)
    return get_pics_stats_at_date(formatted_date_obj)


@v1.get("/disease_mons_percentage")
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

@v1.get("/location-history-dates", status_code=status.HTTP_200_OK, response_model=LocationHistoryModel)
async def get_location_history_dates(
    token: str = Depends(get_token_auth_header),
    zone_id: str = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...)
):
    print("HHHHHHH")
    try:
        # Convert input date strings to datetime objects
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y") + timedelta(days=1) - timedelta(seconds=1) # ensure the entire day is included
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use d-m-Y.")

    try:
        # Fetch all period_of_disease documents for the given zone_id created after the from_date
        periods =  period_of_disease_collection.find({
            "zoneId": ObjectId(zone_id),
            "dateCreated": {"$gte": start_datetime}
        })
        periods = list(periods)
        
        if not periods:
            return {"success": True, "data": {"allHistory": []}}

        # Get all period_of_disease ids
        period_ids = [str(period["_id"]) for period in periods]

        # Fetch all images related to the periods within the specified date range
        images = images_collection.find({
            "PeriodOfDiseaesId": {"$in": period_ids},
            "Date": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        })
        images = list(images)
        # print("images",images)
        # Convert ObjectId to string and return the documents
        result = []
        for image in images:
            location = image.get("Location")
            # First, try to get treatment by location
            

            # Calculate mean confidence percentage
            confidences = image.get("Confidence", [])
            mean_confidence = np.mean(confidences) if confidences else 0

            # Construct item data
            date_str = image.get("Date").strftime("%d-%m-%Y")
            item_data = {
                "itemImageSrc": transform(image.get("Image_Path", "")),
                "thumbnailImageSrc": transform(image.get("Resized_Path", "")),
                "alt": f"{mean_confidence:.2f}%",
                "title": date_str
            }
            result.append(item_data)

        # Return the response using LocationHistoryModel
        all_locs = [LocationHistory(**item) for item in result]
        all_locs_lst = LocationHistoryList(allHistory=all_locs)
        return LocationHistoryModel(success=True, data=all_locs_lst)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

from datetime import datetime

@v1.get("/get-date-per-diseased-plants", status_code=status.HTTP_200_OK, response_model=DatePerDiseasedPlantsResponse)
async def get_date_per_diseased_plants(token: str = Depends(get_token_auth_header), zone_id: str = Query(...)):
    try:
        # Fetch all periods of disease for the given zone_id
        periods = list(period_of_disease_collection.find({"zoneId": ObjectId(zone_id)}))
        # print("periods", periods)
        # Initialize lists to store dates and percentages
        unique_dates = []
        percentages = []

        # Iterate over each period
        for period in periods:
            # Get the period ID
            period_id = str(period["_id"])
            print("period_id", period_id)
            # Get unique dates for the current period
            dates = images_collection.distinct("Date", {"PeriodOfDiseaesId": period_id})
            print("dates", dates)
            # Iterate over each date in the period
            for date in dates:
                # Count total number of images for this date and period
                total_images = images_collection.count_documents({"PeriodOfDiseaesId": period_id, "Date": date})
                print("total_images", total_images)
                # Count number of diseased images (Image_Class 0 or 1) for this date and period
                diseased_images = images_collection.count_documents({"PeriodOfDiseaesId": period_id, "Date": date, "Image_Class": {"$in": [0, 1]}})
                
                # Calculate percentage and store results for this date
                if total_images > 0:
                    unique_dates.append(date.strftime("%d-%m-%Y"))
                    percentages.append(diseased_images * 100 / total_images)

        # Return the response
        return DatePerDiseasedPlantsResponse(success=True, data=DatePerDiseasedPlants(dates=unique_dates, percentages=percentages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@v1.get("/get-blight-images-percentage", status_code=status.HTTP_200_OK, response_model=DataResponseStatistics)
async def get_blight_images_percentage(date: str = Query(...), token: str = Depends(get_token_auth_header)):
    try:
        # Convert date string to datetime object
        date_obj = datetime.strptime(date, "%d-%m-%Y")
        start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        # Count total number of images for the given date
        images_count = images_collection.count_documents({
            "Date": {"$gte": start_date, "$lt": end_date}
        })

        # Count number of Early Blight (EB) and Late Blight (LB) images for the given date
        EB_count = images_collection.count_documents({
            "Date": {"$gte": start_date, "$lt": end_date},
            "Image_Class": 0
        })
        LB_count = images_collection.count_documents({
            "Date": {"$gte": start_date, "$lt": end_date},
            "Image_Class": 1
        })

        # Calculate percentages
        EB_percentage = (EB_count / images_count) * 100 if images_count > 0 else 0
        LB_percentage = (LB_count / images_count) * 100 if images_count > 0 else 0

        # Define diseases and percentages
        diseases = ["Early blight", "Late blight"]
        percentages = [int(EB_percentage), int(LB_percentage)]

        # Return the response
        return DataResponseStatistics(success=True, data=DiseasesResponse(diseases=diseases, percentages=percentages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





