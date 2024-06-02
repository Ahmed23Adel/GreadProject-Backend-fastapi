from pydantic import BaseModel, Field
from typing import List
    
class ZoneData(BaseModel):
    zoneId: str = Field(..., description="The ID of the zone")
    name: str = Field(..., description="The name of the zone")

class ZoneResponse(BaseModel):
    success: bool
    data: List[ZoneData]