from src.basic import *
from typing import Optional

# Helper function to convert date format
def convert_date_format(selected_date):
    try:
        converted_date = datetime.strptime(selected_date, "%d-%m-%Y").strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
        return converted_date
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use format d-m-Y.")

# Helper function to get zone id from zone name
def get_zone_id(zone_name):
    zone = zones_collection.find_one({"zoneName": zone_name})
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone with name {zone_name} not found")
    return str(zone["_id"])

# Helper function to get period of disease ids by zone id
def get_period_of_disease_ids(zone_id):
    period_of_diseases = period_of_disease_collection.find({"zoneId": ObjectId(zone_id)})
    return [str(period["_id"]) for period in period_of_diseases]

def get_images_by_period_of_disease(period_of_disease_id, is_healthy=None, is_eb=None, is_lb=None, converted_date=None):
    images = []
    query = {"PeriodOfDiseaesId": period_of_disease_id}
    if is_healthy is not None:
        query["Image_Class"] = 2 if is_healthy else {"$in": [0, 1]}
    elif is_eb is not None:
        query["Image_Class"] = 0 if is_eb else {"$ne": 0}
    elif is_lb is not None:
        query["Image_Class"] = 1 if is_lb else {"$ne": 1}
    if converted_date:
        converted_date = datetime.strptime(converted_date, "%Y-%m-%dT%H:%M:%S.%f+00:00")
        query["Date"] = {"$eq": converted_date}
    cursor = images_collection.find(query)
    for image in cursor:
        # Get the period of disease associated with the image
        period_of_disease = period_of_disease_collection.find_one({"_id": ObjectId(period_of_disease_id)})
        if period_of_disease:
            zone_id = period_of_disease.get("zoneId")
            if zone_id:
                zone = zones_collection.find_one({"_id": zone_id})
                if zone:
                    image["ZoneName"] = zone.get("zoneName")
                    image["Location"] = zone.get("zoneName")  # Adding location attribute
        images.append(image)
    return images

def count_images_by_filters(is_healthy=None, is_eb=None, is_lb=None, converted_date=None):
    query = {}
    if is_healthy is not None:
        query["Image_Class"] = 2 if is_healthy else {"$in": [0, 1]}
    elif is_eb is not None:
        query["Image_Class"] = 0 if is_eb else {"$ne": 0}
    elif is_lb is not None:
        query["Image_Class"] = 1 if is_lb else {"$ne": 1}
    if converted_date:
        converted_date = datetime.strptime(converted_date, "%Y-%m-%dT%H:%M:%S.%f+00:00")
        query["Date"] = {"$eq": converted_date}
    return images_collection.count_documents(query)

# Endpoint to get summary
@v1.get('/get_summary')
def get_summary(
    selected_date: Optional[str] = None,
    selected_location: Optional[str] = None,
    is_healthy: Optional[bool] = None,
    is_eb: Optional[bool] = None,
    is_lb: Optional[bool] = None,
    index: int = 0
):
    # Convert selected date format
    converted_date = None
    if selected_date:
        converted_date = convert_date_format(selected_date)
    print("selected_date", selected_date, converted_date)
    # Get zone id if selected location is provided
    zone_id = get_zone_id(selected_location) if selected_location else None

    # Get period of disease ids by zone id
    period_of_disease_ids = get_period_of_disease_ids(zone_id) if zone_id else []

    # Calculate offset for paging
    page_size = 20
    offset = index * page_size

    # Count total number of images for the filters
    total_images = 0
    if period_of_disease_ids:
        for period_id in period_of_disease_ids:
            query = {"PeriodOfDiseaesId": period_id}
            if converted_date:
                query["Date"] = datetime.strptime(converted_date, "%Y-%m-%dT%H:%M:%S.%f+00:00")
            total_images += images_collection.count_documents(query)
    else:
        total_images = count_images_by_filters(is_healthy, is_eb, is_lb, converted_date)

    # Calculate max index for pagination
    max_index = (total_images - 1) // page_size

    # Get images by period of disease ids and optional filters
    all_images = []
    unique_period_of_disease_ids = set()

    if not any([selected_date, selected_location, is_healthy, is_eb, is_lb]):
        # No filters provided, return all data
        cursor = images_collection.find()
        for image in cursor:
            period_of_disease_id = image.get("PeriodOfDiseaesId")
            if period_of_disease_id:
                unique_period_of_disease_ids.add(period_of_disease_id)
    else:
        for period_id in period_of_disease_ids:
            unique_period_of_disease_ids.add(period_id)

    # Fetch images for unique period of disease IDs
    for period_id in unique_period_of_disease_ids:
        all_images.extend(get_images_by_period_of_disease(period_id, is_healthy, is_eb, is_lb, converted_date))

    # Apply paging to the combined list of images
    paginated_images = all_images[offset:offset + page_size]

    # Convert ObjectId to string representation in each document
    summary_data = [{**image, "_id": str(image.get('_id'))} for image in paginated_images]

    # Get all zone names
    all_zones = [zone['zoneName'] for zone in zones_collection.find()]

    # Return summary data along with all zone names and max index for paging
    return {
        "success": True,
        'data': {
            "summary_data": summary_data,
            "all_zones": all_zones,
            "max_page_size": page_size,
            "max_index": max_index
        }
    }
