from pydantic import BaseModel
from typing import List

class UserData(BaseModel):
    user_id: str

class RegisterResponse(BaseModel):
    success: bool
    data: UserData

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "user_id": "60c85a29d2a7e62156aa0f32"
                }
            }
        }

from pydantic import BaseModel

class LoginData(BaseModel):
    user_type: str
    user_id: str
    token: str

class LoginResponse(BaseModel):
    success: bool
    data: LoginData

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "user_type": "expert",
                    "user_id": "60c85a29d2a7e62156aa0f32",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            }
        }


from pydantic import BaseModel

class ActivateUserData(BaseModel):
    user_id: str
    activated: bool

class ActivateUserResponse(BaseModel):
    success: bool
    data: ActivateUserData

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "user_id": "60c85a29d2a7e62156aa0f32",
                    "activated": True
                }
            }
        }

class UserData(BaseModel):
    _id: str
    user_name: str
    activated: bool
    type: str

class UsersResponse(BaseModel):
    users: List[UserData]