from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum
from typing import Optional
from src.bookings.booking_models import BookingStatus

from src.coaches.coach_schemas import CoachMeOut, SlotOut





class BookingBase(BaseModel):
    # NOTE: user_id removed — user is taken from the authenticated `current` user
    status: BookingStatus = BookingStatus.scheduled
    notes: Optional[str] = Field(default=None, max_length=500)



class BookingCreate(BookingBase):
    slot_id: int



class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = Field(default=None, max_length=500)



class BookingResponse(BookingBase):
    id: int
    coach_id: int
    slot_id: Optional[int]
    start_time: datetime
    end_time: datetime
    price: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class BookingDetailedResponse(BookingResponse):
    coach: Optional[CoachMeOut]
    slot: Optional[SlotOut]



class CoachBookingResponse(BookingResponse):
    slot: Optional[SlotOut]