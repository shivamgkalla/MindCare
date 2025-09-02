from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from src.users.user_schemas import GenderEnum



class CoachProfileBase(BaseModel):
    qualifications: str = Field(..., max_length=500)
    specialization: str = Field(..., max_length=200)
    experience_years: int = Field(..., gt=0, lt=60)
    charges_per_slot: Optional[float] = Field(default=None, gt=0)
    availability_status: Optional[bool] = True



class CoachProfileCreate(CoachProfileBase):
    pass



class CoachProfileUpdate(BaseModel):
    qualifications: Optional[str] = Field(default=None, max_length=500)
    specialization: Optional[str] = Field(default=None, max_length=200)
    experience_years: Optional[int] = Field(default=None, gt=0, lt=60)
    charges_per_slot: Optional[float] = Field(default=None, gt=0)
    availability_status: Optional[bool] = None



class CoachProfileOut(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    qualifications: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    charges_per_slot: Optional[float] = None
    availability_status: Optional[bool] = None


    model_config = ConfigDict(from_attributes=True)



class CoachMeOut(BaseModel):
 # Combined user + coach profile for convenience
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
    coach_profile: Optional[CoachProfileOut] = None


    model_config = ConfigDict(from_attributes=True)



# --- Slot Schemas ---
class CoachSlotBase(BaseModel):
    date: str = Field(..., examples=["2025-08-30"])
    start_time: str = Field(..., examples=["14:00"])  # HH:MM
    end_time: str = Field(..., examples=["15:00"])  # HH:MM
    price: Optional[float] = Field(default=None, ge=0)


class CoachSlotCreate(CoachSlotBase):
    pass



class CoachSlotUpdate(BaseModel):
    date: Optional[str] = Field(default=None, examples=["2025-08-30"])
    start_time: Optional[str] = Field(default=None, examples=["14:00"])  # HH:MM
    end_time: Optional[str] = Field(default=None, examples=["15:00"])    # HH:MM
    price: Optional[float] = Field(default=None, ge=0)




class CoachSlotResponse(CoachSlotBase):
    id: int
    coach_id: int
    start_time: str = Field(..., examples=["16:00"])  # HH:MM
    end_time: str = Field(..., examples=["17:00"])    # HH:MM
    price: Optional[float] = None
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)



# ----------------------
# SlotOut Schema
# ----------------------
class SlotOut(BaseModel):
    slot_id: int
    date: str = Field(..., examples=["2025-08-31"])
    start_time: str = Field(..., examples=["16:00"])  # HH:MM
    end_time: str = Field(..., examples=["17:00"])    # HH:MM
    price: Optional[float] = None
    duration_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)




class CoachBrowseOut(CoachMeOut):
    # slots: List[CoachSlotResponse] = Field(default_factory=list)
    available_slots: List[SlotOut] = Field(default_factory=list)