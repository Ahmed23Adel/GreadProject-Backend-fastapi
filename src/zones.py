from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.zonesModels import ZoneResponse
from typing import List

print("Intializing zones")
BASE_URL = "zones"

    

@v1.get("/get-all-zones", response_model=ZoneResponse, status_code=status.HTTP_200_OK)
def get_all_zones(token: str = Depends(get_token_auth_header)):
    zones = list(zones_collection.find())
    print("zonesll", zones)
    zones = [{"zoneId": str(zone["_id"]), "name": zone["zoneName"]} for zone in zones]
    return {"success": True, "data": zones}

    





