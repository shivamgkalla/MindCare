from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from src.users.user_schemas import GenderEnum
from src.coaches.coach_schemas import CoachProfileOut


class AdminUserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str   # "user" or "coach"
    phone_number: Optional[str] = None
    password: str



class AdminCoachProfileOut(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    qualifications: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    charges_per_slot: Optional[float] = None
    availability_status: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)



class AdminProfileOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    is_verified: bool
    is_active: bool
    role: str
    coach_profile: Optional[AdminCoachProfileOut] = None


    model_config = ConfigDict(from_attributes=True)



