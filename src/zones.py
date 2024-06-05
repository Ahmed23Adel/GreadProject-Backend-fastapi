from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.zonesModels import ZoneResponse
from typing import List
from src.zonesModels import (
    NewZoneRequest
)

print("Intializing zones")
BASE_URL = "zones"

    

@v1.get("/get-all-zones", response_model=ZoneResponse, status_code=status.HTTP_200_OK)
def get_all_zones(token: str = Depends(get_token_auth_header)):
    zones = list(zones_collection.find())
    print("zonesll", zones)
    zones = [{"zoneId": str(zone["_id"]), "name": zone["zoneName"]} for zone in zones]
    return {"success": True, "data": zones}

   
@v1.post("/create-new-zone", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_new_zone(zone_data: NewZoneRequest, token: str = Depends(get_token_auth_header_hardware)):
    try:
        # Check if the zone name already exists
        existing_zone = zones_collection.find_one({"zoneName": zone_data.zone_name})
        if existing_zone:
            raise HTTPException(status_code=400, detail="Zone name already exists")

        # Extract the zone number from the zone name
        zone_number = extract_zone_number(zone_data.zone_name)

        # If zone number extraction failed, raise an exception
        if zone_number is None:
            raise HTTPException(status_code=400, detail="Invalid zone name format. Zone name must be in the format 'Zone x' where 'x' is an integer.")

        # Insert the new zone into the database
        new_zone = {
            "zoneName": zone_data.zone_name
        }
        zones_collection.insert_one(new_zone)

        return {"success": True, "data": {}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def extract_zone_number(zone_name: str) -> int:
    try:
        # Split the zone name by space and extract the last part
        zone_name_parts = zone_name.split(" ")
        if (not len(zone_name_parts) == 2): return None
        if (not zone_name_parts[0] == "Zone"): return None
        zone_number_str = zone_name.split(" ")[-1]
        # Convert the extracted part to an integer
        zone_number = int(zone_number_str)
        return zone_number
    except ValueError:
        return None
    
@v1.get("/get-diseased-zones", response_model=ZoneResponse)
async def get_open_zones(token: str = Depends(get_token_auth_header)):
    try:
        # Fetch all period_of_disease documents with dateEnded not set
        open_periods = period_of_disease_collection.find({
            "$or": [
                {"dateEnded": {"$exists": False}},
                {"dateEnded": None}
            ]
        })
        open_zone_ids = {period["zoneId"] for period in open_periods}
        if not open_zone_ids:
            return {"success": True, "data": []}

        # Fetch all zones with _id in open_zone_ids
        open_zones = zones_collection.find({"_id": {"$in": list(open_zone_ids)}})
        print("open_zone_ids", open_zone_ids)
        zones_list = []
        for zone in open_zones:
            # Determine isLocationNewForExpert by checking if approverExpertId exists in period_of_disease_collection
            curr_period = period_of_disease_collection.find_one({"zoneId": zone["_id"], "dateEnded": None}, {"approverExpertId": 1, "specificTreatmentId": 1, "currentDisease": 1})
            # is_location_new = false
            # print("curr_period", curr_period)
            is_location_new = True
            print("before try")
            try:
                approver_expert_id = curr_period['approverExpertId']
                is_location_new  = False
                print("approver_expert_id", approver_expert_id)
                print(not approver_expert_id or approver_expert_id == "")
                if not approver_expert_id or approver_expert_id == "" : is_location_new = True
                else: is_location_new = False
                print("last try")
            except:
                is_location_new = True
            # print("is_location_new", is_location_new)
            # Determine zonesTreatment
            try:
                specific_treatment_id = curr_period['specificTreatmentId']
                print("There is specific_treatment_id")
                treatment_description = get_treatment_description(specific_treatment_id)
                print("treatment_description", treatment_description)
            except:
                current_disease = curr_period.get("currentDisease")
                print("current_disease", current_disease)
                treatment_description = get_default_treatment_description(current_disease)

            zones_list.append({
                "id": str(zone["_id"]),
                "activePeriodOfDisease": str(curr_period["_id"]), 
                "zoneName": zone["zoneName"],
                "isLocationNewForExpert": is_location_new,
                "zonesTreatment": treatment_description
            })
            print("---------------------------------------------------------------- ")
        return {"success": True, "data": {"locations": zones_list}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_treatment_description(treatment_id: str):
    # Connect to your MongoDB database and collection
    # Implement logic to fetch treatment description from treatment collection using treatment_id
    print("in get_treatment_description", treatment_id)
    treatment = saved_treatment_schedule_collection.find_one({"_id": ObjectId(treatment_id)})
    if treatment:
        return treatment.get("treatmentDescription", "")
    else:
        return ""

def get_default_treatment_description(disease_name: str):
    # Connect to your MongoDB database and collection
    # Implement logic to fetch defaultSavedTreatment description from disease collection using disease_name
    disease = disease_collection.find_one({"diseaseName": disease_name})
    if disease:
        default_treatment_id = disease.get("defaultSavedTreatment")
        if default_treatment_id:
            print("default_treatment_id", default_treatment_id)
            treatment = saved_treatment_schedule_collection.find_one({"_id": ObjectId(default_treatment_id)})
            if treatment:
                return treatment.get("treatmentDescription", "")
    return ""





