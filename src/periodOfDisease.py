from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from src.periodOfDiseaseModels import(
    PeriodOfDiseaseImage,
)

@v1.post("/create_period_of_disease", response_model=dict)
async def create_period_of_disease(
    period_of_disease_image: PeriodOfDiseaseImage,
    token: str = Depends(get_token_auth_header)
):
    try:
        PeriodOfDiseaseImage.validate_zone_id(period_of_disease_image.zoneId)
        PeriodOfDiseaseImage.validate_current_disease(period_of_disease_image.currentDisease)

    
        new_period_of_disease_image = {
            "zoneId": ObjectId(period_of_disease_image.zoneId),
            "dateCreated": period_of_disease_image.dateCreated,
            "dateApprovedByExpert": period_of_disease_image.dateApprovedByExpert,
            "approverExpertId": period_of_disease_image.approverExpertId,
            "dateEnded": period_of_disease_image.dateEnded,
            "enderExpertId": period_of_disease_image.enderExpertId,
            "currentDisease": period_of_disease_image.currentDisease,
            "specificTreatmentId": period_of_disease_image.specificTreatmentId,
        }

        period_of_disease_collection.insert_one(new_period_of_disease_image)

        return {"success": True, "data": {}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
from datetime import datetime

@v1.put("/set-zone-checked", response_model=dict)
async def set_zone_checked(
    period_of_disease_id: str,
    expert_id: str,
    token: str = Depends(get_token_auth_header)
):
    try:
        # Fetch the period of disease document
        period_of_disease = period_of_disease_collection.find_one({"_id": ObjectId(period_of_disease_id)})
        if not period_of_disease:
            raise HTTPException(status_code=404, detail="Period of disease not found")
        
        # Update the period of disease document
        current_date =  datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        period_of_disease_collection.update_one(
            {"_id": ObjectId(period_of_disease_id)},
            {
                "$set": {
                    "dateApprovedByExpert": current_date,
                    "approverExpertId": expert_id
                }
            }
        )

        return {"success": True, "message": "Zone checked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
