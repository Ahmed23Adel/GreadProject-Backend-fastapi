from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from src.basic import *

class PeriodOfDiseaseImage(BaseModel):
    zoneId: str
    dateCreated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    dateApprovedByExpert: Optional[datetime] = None
    approverExpertId: Optional[str] = None
    dateEnded: Optional[datetime] = None
    enderExpertId: Optional[str] = None
    currentDisease: str
    specificTreatmentId: Optional[str] = None

    @classmethod
    def validate_zone_id(cls, zone_id: str):
        if not ObjectId.is_valid(zone_id) or not zones_collection.find_one({"_id": ObjectId(zone_id)}):
            raise HTTPException(status_code=400, detail="Invalid zoneId")

    @classmethod
    def validate_current_disease(cls, disease: str):
        if disease not in ["Early blight", "Late blight"]:
            raise HTTPException(status_code=400, detail="Invalid currentDisease")


