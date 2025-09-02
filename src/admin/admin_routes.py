from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List
from src.admin import admin_services
from src.coaches import coach_services
from src.coaches.coach_schemas import CoachProfileUpdate
from src.database import get_db
from src.users.user_schemas import UserProfileUpdate
from src.users import user_services
from src.auth.auth_services import require_role
from src.admin.admin_schemas import AdminCoachProfileOut, AdminUserCreate, AdminProfileOut
from src.bookings.booking_schemas import BookingResponse
from src.bookings.booking_models import Booking
from src.journals.journal_models import Journal
from src.journals.journal_schemas import JournalOut



router = APIRouter(
    prefix = "/admin",
    tags = ["Admin"],
)


db_dependency = Annotated[Session, Depends(get_db)]



@router.get("/profiles", response_model=List[AdminProfileOut], status_code=status.HTTP_200_OK)
def list_profiles(db: db_dependency, current=Depends(require_role(["admin"])), role: Optional[str] = Query(None)):
    return admin_services.list_profiles(db, role)


@router.get("/profiles/{user_id}", response_model=AdminProfileOut, status_code=status.HTTP_200_OK)
def get_profile(db: db_dependency, user_id: int, current=Depends(require_role(["admin"]))):
    return admin_services.get_profile(db, user_id)



@router.post("/profiles/", response_model=AdminProfileOut, status_code=status.HTTP_201_CREATED)
def create_user_via_admin(db: db_dependency, payload: AdminUserCreate, current=Depends(require_role(["admin"]))):
    return admin_services.create_user_as_admin(db, payload)



@router.put("/user/profiles/{user_id}", response_model=AdminProfileOut, status_code=status.HTTP_200_OK)
def admin_update_user_profile(db: db_dependency, user_id: int, payload: UserProfileUpdate, current=Depends(require_role(["admin"]))):
    user_services.admin_update_profile(db, user_id, payload)
    return admin_services.get_profile(db, user_id)



@router.put("/coaches/profile/{user_id}", response_model=AdminCoachProfileOut, status_code=status.HTTP_200_OK)
def admin_update_coach_profile(db: db_dependency, user_id: int, payload: CoachProfileUpdate, current=Depends(require_role(["admin"]))):
    """Admin updates an existing coach profile"""
    coach = coach_services.create_or_update_profile(db, user_id, payload)
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach profile not found.")
    return AdminCoachProfileOut.model_validate(coach)



@router.get("/bookings/{user_id}", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
def admin_get_all_bookings(db: db_dependency, user_id: int, current=Depends(require_role(["admin"]))):
    """Admin fetches all bookings"""
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings



@router.get("/journals/{user_id}", response_model=List[JournalOut], status_code=status.HTTP_200_OK)
def admin_get_all_journals(db: db_dependency, user_id: int, current=Depends(require_role(["admin"]))):
    """Admin fetches all user journals"""
    journals = db.query(Journal).filter(Journal.user_id == user_id).all()
    return journals



@router.delete("/profiles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(db: db_dependency, user_id: int, current=Depends(require_role(["admin"]))):
    admin_services.delete_profile(db, user_id)
    return



@router.get("/", response_model=List[BookingResponse])
def admin_list_bookings(db: db_dependency, current=Depends(require_role(["admin"]))):
    return admin_services.list_all_bookings(db)