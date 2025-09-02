from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import List, Optional
from src.bookings.booking_models import Booking, BookingStatus, CoachSlot
from src.bookings.booking_schemas import BookingCreate, BookingUpdate, BookingDetailedResponse, CoachBookingResponse
from src.coaches.coach_schemas import CoachMeOut
from src.coaches import coach_services



def create_booking(db: Session, booking_data: BookingCreate, user_id: int) -> Booking:
    slot: Optional[CoachSlot] = db.query(CoachSlot).filter(CoachSlot.id == booking_data.slot_id).first()

    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found for this coach.")

    if slot.is_booked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This slot is already booked.")


    new_booking = Booking(
        user_id = user_id,
        coach_id = slot.coach_id,
        slot_id = slot.id,
        start_time = slot.start_time,
        end_time = slot.end_time,
        status = BookingStatus.scheduled,
        notes = booking_data.notes,
        price = slot.price
    )

    slot.is_booked = True
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking



def get_booking_by_id(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).options(joinedload(Booking.coach), joinedload(Booking.slot)).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
 
    return booking



def get_user_bookings(db: Session, user_id: int, status: Optional[BookingStatus] = None, upcoming: bool = True) -> List[Booking]:
    query = db.query(Booking).options(joinedload(Booking.coach), joinedload(Booking.slot)).filter(Booking.user_id == user_id)
    if status:
        query = query.filter(Booking.status == status)
        
    if upcoming:
        query = query.filter(Booking.start_time > datetime.now(timezone.utc))
    
    return query.all()



def update_booking(db: Session, booking_id: int, booking_data: BookingUpdate, user_id: int) -> Booking:
    booking = get_booking_by_id(db, booking_id)

    if booking.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this booking.")

    if booking_data.notes is not None:
        booking.notes = booking_data.notes

    if booking_data.status is not None:
        booking.status = booking_data.status
        # Free up slot if cancelled
        if booking.status == BookingStatus.cancelled and booking.slot:
            booking.slot.is_booked = False
        
    db.commit()
    db.refresh(booking)
    return booking



def delete_booking(db: Session, booking_id: int, user_id: int):
    booking = get_booking_by_id(db, booking_id)

    if booking.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this booking.")

    # Free up slot if booked.
    if booking.slot and booking.status != BookingStatus.completed:
        booking.slot.is_booked = False

    db.delete(booking)
    db.commit()
    return {"detail": "Booking deleted successfully"}



# ----------------------
# Admin Related Endpoints
# ----------------------

def admin_list_all_bookings(
    db: Session, 
    status_filter: Optional[BookingStatus] = None, 
    coach_id: Optional[int] = None, 
    user_id: Optional[int] = None, 
    skip: int = 0,
    limit: int = 20
    ) -> List[Booking]:

    query = db.query(Booking)

    if status_filter:
        query = query.filter(Booking.status == status_filter)

    if coach_id:
        query = query.filter(Booking.coach_id == coach_id)

    if user_id:
        query = query.filter(Booking.user_id == user_id)

    return query.offset(skip).limit(limit).all()



def admin_get_booking(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    return booking



# Formatter for BookingDetailedResponse
def format_booking_detailed(booking: Booking) -> BookingDetailedResponse:
    return BookingDetailedResponse(
        id=booking.id,
        coach_id=booking.coach_id,
        slot_id=booking.slot.id if booking.slot else None,
        start_time=booking.slot.start_time if booking.slot else None,
        end_time=booking.slot.end_time if booking.slot else None,
        price=booking.slot.price if booking.slot else None,
        created_at=booking.created_at,
        status=booking.status,
        notes=booking.notes,
        coach=CoachMeOut.model_validate(booking.coach) if booking.coach else None,
        slot=coach_services.format_slot_for_public(booking.slot) if booking.slot else None,
    )



# Formatter for CoachBookingResponse
def format_coach_booking(booking: Booking) -> CoachBookingResponse:
    return CoachBookingResponse(
        id=booking.id,
        coach_id=booking.coach_id,
        slot_id=booking.slot.id if booking.slot else None,
        start_time=booking.slot.start_time if booking.slot else None,
        end_time=booking.slot.end_time if booking.slot else None,
        price=booking.slot.price if booking.slot else None,
        created_at=booking.created_at,
        status=booking.status,
        notes=booking.notes,
        coach=CoachMeOut.model_validate(booking.coach) if booking.coach else None,
        slot=coach_services.format_slot_for_public(booking.slot) if booking.slot else None,
    )



# ----------------------
# Coach Services
# ----------------------

def coach_list_all_bookings(
    db: Session,
    coach_id: int,
    status: Optional[BookingStatus] = None,
    upcoming: Optional[bool] = True,
    skip: int = 0,
    limit: int = 20,
    ) -> List[Booking]:

    """Return bookings for a specific coach, with optional filters"""
    query = db.query(Booking).filter(Booking.coach_id == coach_id)

    if status:
        query = query.filter(Booking.status == status)

    if upcoming:
        query = query.filter(Booking.start_time >= datetime.now(timezone.utc))


    return query.offset(skip).limit(limit).all()



def get_coach_booking(db: Session, coach_id: int, booking_id: int) -> Booking:
    """Return a single booking if it belongs to the coach."""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.coach_id == coach_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not authorized")

    return booking