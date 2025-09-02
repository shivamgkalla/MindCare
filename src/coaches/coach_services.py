from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from typing import List, Optional
from src.coaches.coach_models import CoachProfile
from src.bookings.booking_models import Booking, BookingStatus, CoachSlot
from src.coaches.coach_schemas import CoachProfileCreate, CoachProfileUpdate, CoachSlotCreate, CoachSlotUpdate, CoachBrowseOut, CoachSlotResponse, SlotOut
from src.auth.auth_models import Users




def get_coach_me(db: Session, user_id: int) -> Users:
    user = db.query(Users).filter(Users.id == user_id, Users.role == "coach").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found or role mismatch")
    return user



def create_or_update_profile(db: Session, user_id: int, payload: CoachProfileCreate | CoachProfileUpdate) -> CoachProfile:
    coach = db.query(CoachProfile).filter(CoachProfile.user_id == user_id).first()

    if not coach:
        # Create Coach Profile
        if isinstance(payload, CoachProfileUpdate):
            # For creation, we need required fields; ensure present
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coach does not exist, Use create payload.")
        coach = CoachProfile(user_id = user_id, **payload.model_dump())
        db.add(coach)

    else:
        # Update Coach Profile
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(coach, key, value)
        db.add(coach)
    
    db.commit()
    db.refresh(coach)
    return coach



def set_availability(db: Session, user_id: int, is_available: bool) -> CoachProfile:
    coach = db.query(CoachProfile).filter(CoachProfile.user_id == user_id).first()
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach profile not found")
    coach.availability_status = is_available
    db.add(coach)
    db.commit()
    db.refresh(coach)
    return coach


# Admin utilities
def admin_list_profiles(db: Session, role: str | None = None):
    query = db.query(Users)
    if role:
        query = query.filter(Users.role == role)
    return query.all()



def get_coach_by_user_id(db: Session, user_id: int) -> CoachProfile | None:
    """
    Fetch the coach profile linked to a given user_id.
    Returns None if not found.
    """
    return db.query(CoachProfile).filter(CoachProfile.user_id == user_id).first()



# -------------------------
# Slot Services
# -------------------------

def create_coach_slot(db: Session, coach_id: int, payload: CoachSlotCreate) -> CoachSlot:
    
    # Parse date + times
    slot_date = datetime.strptime(payload.date, "%Y-%m-%d").date()
    start_time = datetime.strptime(payload.start_time, "%H:%M").time()
    end_time = datetime.strptime(payload.end_time, "%H:%M").time()

    # Merge into timezone-aware datetimes 
    start_dt = datetime.combine(slot_date, start_time).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(slot_date, end_time).replace(tzinfo=timezone.utc)

    # Validation
    if end_dt <= start_dt:
        raise ValueError("End time must be after start time.")

    slot = CoachSlot(coach_id = coach_id, start_time = start_dt, end_time = end_dt, price = payload.price)

    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    return slot



def get_slots_by_coach(db: Session, coach_id: int) -> List[CoachSlot]:
    return db.query(CoachSlot).filter(CoachSlot.coach_id == coach_id).all()



def update_coach_slot(db: Session, slot_id: int, coach_id: int, payload: CoachSlotUpdate) -> CoachSlot:
    slot = db.query(CoachSlot).filter(CoachSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")

    if slot.coach_id != coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this slot")


    # Only update fields that are provided
    if payload.date or payload.start_time or payload.end_time:
        # Use existing values if not provided
        slot_date = datetime.strptime(payload.date, "%Y-%m-%d").date() if payload.date else slot.start_time.date()
        start_t = datetime.strptime(payload.start_time, "%H:%M").time() if payload.start_time else slot.start_time.time()
        end_t = datetime.strptime(payload.end_time, "%H:%M").time() if payload.end_time else slot.end_time.time()

        start_dt = datetime.combine(slot_date, start_t).replace(tzinfo=timezone.utc)
        end_dt = datetime.combine(slot_date, end_t).replace(tzinfo=timezone.utc)

        if end_dt <= start_dt:
            raise ValueError("End time must be after start time.")

        slot.start_time = start_dt
        slot.end_time = end_dt

    if payload.price is not None:
        slot.price = payload.price

    db.commit()
    db.refresh(slot)
    return slot



def delete_slot(db: Session, coach_id: int, slot_id: int):
    slot = db.query(CoachSlot).filter(CoachSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")
    
    if slot.coach_id != coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delet this slot")

    if slot.is_booked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a booked slot.")


    db.delete(slot)
    db.commit()
    return {"detail": "Slot deleted successfully"}


# ----------------------
# Coach Custom Services
# ----------------------

# Formatter for SlotOut
def format_slot_for_public(slot) -> SlotOut:
    duration = int((slot.end_time - slot.start_time).total_seconds() // 60)

    return SlotOut(
        slot_id=slot.id,
        date=slot.start_time.date().isoformat(),
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
        price=slot.price,
        duration_minutes=duration
    )




# Formatter for CoachSlotResponse
def format_slot_for_me(slot) -> CoachSlotResponse:
    return CoachSlotResponse(
        id=slot.id,
        coach_id=slot.coach_id,
        date=slot.start_time.date().isoformat(),
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
        price=slot.price,
        is_booked=slot.is_booked
    )




def browse_coaches(db: Session, specialization: Optional[str] = None, available_only: bool = False) -> List[Users]:
    """
    Browse coaches with optional filters.
    Attach available slots for each.
    """

    query = select(Users).join(CoachProfile).where(Users.role == "coach")

    if specialization:
        query = query.where(CoachProfile.specialization.ilike(f"%{specialization}%"))

    if available_only:
        query = query.where(CoachProfile.availability_status.is_(True))

    coaches = db.scalars(query).all()

    result: List[CoachBrowseOut] = []
    for coach in coaches:
        available_slots = get_available_slots_for_coach(db, coach.id)
        coach_schema = CoachBrowseOut.model_validate(coach, from_attributes=True)
        coach_schema.available_slots = available_slots
        result.append(coach_schema)

    return result



def get_coach_with_slots(db: Session, coach_id: int) -> Optional[Users]:
    """
    Fetch a single coach with their profile, unbooked slots, and available_slots.
    """

    coach = db.get(Users, coach_id)

    if not coach or coach.role != "coach":
        return None

    # Attach only unbooked slots (raw DB models) under .slots
    slots = (db.query(CoachSlot).filter(CoachSlot.coach_id == coach_id, CoachSlot.is_booked.is_(False)).all())

    coach.slots = slots

    # Attach "available_slots" (typed SlotOut) using helper
    coach.available_slots = get_available_slots_for_coach(db, coach_id, limit=5)

    return coach
   


def get_available_slots_for_coach(db: Session, coach_id: int, limit: int = 5):
    now = datetime.now(timezone.utc)

    slots = (
        db.query(CoachSlot)
        .filter(CoachSlot.coach_id == coach_id,
        CoachSlot.start_time > now,  # Only future-slots
        CoachSlot.is_booked.is_(False))  # Only unbooked
        .order_by(CoachSlot.start_time)
        .limit(limit)
        .all()
    )

    # Convert ORM objects to SlotOut via formatter helper function
    return [format_slot_for_public(s) for s in slots]