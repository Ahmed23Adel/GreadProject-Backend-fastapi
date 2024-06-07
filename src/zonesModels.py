from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, validator

class ZoneData(BaseModel):
    zoneId: str = Field(..., description="The ID of the zone")
    name: str = Field(..., description="The name of the zone")

class ZoneResponse(BaseModel):
    success: bool
    data: List[ZoneData]
    
    
class Zone(BaseModel):
    id: str
    zoneName: str
    activePeriodOfDisease: str
    isLocationNewForExpert: bool
    zonesTreatment: str

class ZoneResponse(BaseModel):
    success: bool
    data: dict

class NewZoneRequest(BaseModel):
    zone_name: str
    
    
class Zone(BaseModel):
    name: str

# Example Pydantic model for period of disease data
class PeriodOfDisease(BaseModel):
    zone_id: str
    date_started: datetime
    date_ended: datetime = None
    
class ZoneInput(BaseModel):
    zone_name: str
    current_disease: str
    
    @validator('current_disease')
    def validate_current_disease(cls, v):
        if v not in {"Early blight", "Late blight"}:
            raise ValueError("Current disease must be either 'Early blight' or 'Late blight'")
        return v

class ZoneNamesInput(BaseModel):
    zones: List[ZoneInput]