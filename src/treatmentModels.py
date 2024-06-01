from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True

class UpdateTreatmentRequest(BaseModel):
    zone_name: str
    specific_treatment: str
