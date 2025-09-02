from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum



class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"



class UserProfileMe(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    phone_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    is_verified: bool
    is_active: bool


    class Config:
        model_config = {"from_attributes": True}




class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    age: Optional[int] = Field(default=None, gt=0, lt=120)
    gender: Optional[GenderEnum] = None
    location: Optional[str] = Field(default=None, max_length=255)