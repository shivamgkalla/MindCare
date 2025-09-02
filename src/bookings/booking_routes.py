from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from src.bookings.booking_models import Booking
from src.database import get_db
from src.auth.auth_services import require_role
from src.bookings.booking_schemas import BookingCreate, BookingStatus, BookingUpdate, BookingResponse, BookingDetailedResponse, CoachBookingResponse
from src.bookings.booking_services import (
    create_booking,
    format_booking_detailed,
    format_coach_booking,
    get_booking_by_id,
    get_user_bookings,
    update_booking,
    delete_booking,
    format_booking_detailed,
    admin_list_all_bookings,
    admin_get_booking,
    coach_list_all_bookings,
    get_coach_booking
)

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

db_dependency = Annotated[Session, Depends(get_db)]

# ----------------------
# Create Booking (User)
# ----------------------
@router.post("/user", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking_route(db: db_dependency, booking_data: BookingCreate, current=Depends(require_role(["user"]))):
    return create_booking(db, booking_data, current.id)



# ----------------------
# Get Current User Bookings
# ----------------------
@router.get("/me/", response_model=List[BookingDetailedResponse], status_code=status.HTTP_200_OK)
def get_my_bookings(db: db_dependency, status: Optional[BookingStatus] = None, upcoming: Optional[bool] = True, current=Depends(require_role(["user"]))):
    booking = get_user_bookings(db, current.id, status, upcoming)
    return [format_booking_detailed(b) for b in booking]




# ----------------------
# Admin Endpoints
# ----------------------

# Admin: List All Bookings
@router.get("/admin", response_model=List[BookingDetailedResponse], status_code=status.HTTP_200_OK)
def admin_list_all_bookings_route(
    db: db_dependency,
    status_filter: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    coach_id: Optional[int] = Query(None, description="Filter by coach"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    skip: int = 0,
    limit: int = 20,
    current=Depends(require_role(["admin"]))):

  bookings = admin_list_all_bookings(db, status_filter, coach_id, user_id, skip, limit)
  return [format_booking_detailed(booking) for booking in bookings]


# Admin: Get Booking Details by ID
@router.get("/admin/{booking_id}", response_model=BookingDetailedResponse, status_code=status.HTTP_200_OK)
def admin_get_booking_route(db: db_dependency, booking_id: int, current=Depends(require_role(["admin"]))):
    booking = admin_get_booking(db, booking_id)
    return format_booking_detailed(booking)



# ----------------------
# Get Booking by ID
# ----------------------
@router.get("/{booking_id}", response_model=BookingDetailedResponse, status_code=status.HTTP_200_OK)
def get_booking_route(db: db_dependency, booking_id: int, current=Depends(require_role(["user"]))):
    booking = get_booking_by_id(db, booking_id)
    return format_booking_detailed(booking)




# ----------------------
# Update Booking (User)
# ----------------------
@router.put("/{booking_id}", response_model=BookingDetailedResponse, status_code=status.HTTP_200_OK)
def update_booking_route(db: db_dependency, booking_id: int, booking_data: BookingUpdate, current=Depends(require_role(["user"]))):
    booking = update_booking(db, booking_id, booking_data, current.id)
    return format_booking_detailed(booking)


# ----------------------
# Delete Booking (User)
# ----------------------
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking_route(db: db_dependency, booking_id: int, current=Depends(require_role(["user"]))):
    delete_booking(db, booking_id, current.id)
    return



# ----------------------
# Coach: View Own Bookings
# ----------------------
@router.get("/coach/", response_model=List[CoachBookingResponse], status_code=status.HTTP_200_OK)
def coach_list_all_bookings_route(
    db: db_dependency,
    status: Optional[BookingStatus] = None,
    upcoming: Optional[bool] = True,
    skip: int = 0,
    limit: int = 20,
    current=Depends(require_role(["coach"]))
):
    bookings = coach_list_all_bookings(
        db=db,
        coach_id=current.id,
        status=status,
        upcoming=upcoming,
        skip=skip,
        limit=limit
    )
    return [format_coach_booking(b) for b in bookings]



# ----------------------
# Coach: Get Booking by ID
# ----------------------
@router.get("/coach/{booking_id}", response_model=CoachBookingResponse, status_code=status.HTTP_200_OK)
def get_coach_booking_route(
    booking_id: int,
    db: db_dependency,
    current=Depends(require_role(["coach"]))
):
    booking = get_coach_booking(db, current.id, booking_id)
    return format_coach_booking(booking)
