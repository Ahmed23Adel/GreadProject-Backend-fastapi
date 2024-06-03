from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query

@v1.get("/moving_car_status", response_model=dict)
async def get_moving_car_status():
    try:
        status_doc = moving_car_status_collection.find_one()
        if not status_doc:
            raise HTTPException(status_code=404, detail="No status found")

        # Remove the _id field from the document
        status_doc.pop("_id", None)

        return {"success": True, "data": status_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))