from fastapi import status, HTTPException, Depends
from src.basic import *
from fastapi import Query
from pydantic import BaseModel, Field
from pydantic import BaseModel, validator

# @v1.get("/moving_car_status", response_model=dict)
# async def get_moving_car_status():
#     try:
#         status_doc = moving_car_status_collection.find_one()
#         if not status_doc:
#             raise HTTPException(status_code=404, detail="No status found")

#         # Remove the _id field from the document
#         status_doc.pop("_id", None)

#         return {"success": True, "data": status_doc}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
    

class UpdateStateInput(BaseModel):
    current_state: int

    @validator('current_state')
    def validate_current_state(cls, v):
        if v not in {0, 1, 2, 3}:
            raise ValueError("current_state must be one of the following values: 0, 1, 2, 3")
        return v

@v1.put("/update_car_state", response_model=dict)
async def update_car_state(update_state_input: UpdateStateInput):
    try:
        result = moving_car_status_collection.update_one(
            {},  # Update the first document found in the collection
            {"$set": {"current_state": update_state_input.current_state}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No document found to update")

        return {"success": True, "message": "Car state updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
class CarStateResponse(BaseModel):
    current_state: int

@v1.get("/get_car_state")
async def get_car_state():
    try:
        # Find the first document in the collection
        car_state_doc = moving_car_status_collection.find_one({}, {"_id": 0, "current_state": 1})

        if not car_state_doc:
            raise HTTPException(status_code=404, detail="No document found")
        return {"success": True, "data":{"current_state": car_state_doc["current_state"]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))