from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from src.database import get_db
from src.auth.auth_services import require_role
from src.auth.auth_models import Users
from src.utils.allowed_roles import ALLOWED_ROLES
from src.utils.file_upload import save_profile_photo
from src.users.user_schemas import UserProfileUpdate
from src.users import user_services
from src.coaches import coach_services, coach_schemas
from src.coaches.coach_schemas import CoachProfileCreate, CoachProfileUpdate, CoachProfileOut, CoachMeOut, CoachSlotCreate, CoachSlotUpdate, CoachSlotResponse, CoachBrowseOut, SlotOut



router = APIRouter(
    prefix = "/coaches",
    tags = ["Coaches"]
)


db_dependency = Annotated[Session, Depends(get_db)]


# ----------------------
# Coach Profile Endpoints
# ----------------------


@router.get("/me", response_model=CoachMeOut)
def get_my_coach_profile(db: db_dependency, current=Depends(require_role(["admin", "coach"]))):

    """Fetch logged-in coach + profile"""
    return coach_services.get_coach_me(db, current.id)



@router.post("/me/profile", response_model=CoachProfileOut, status_code=status.HTTP_201_CREATED)
def create_coach_profile(db: db_dependency, payload: CoachProfileCreate, current=Depends(require_role(["coach", "admin"]))):

    """Create a new coach profile"""
    return coach_services.create_or_update_profile(db, current.id, payload)



@router.put("/me/profile", response_model=CoachProfileOut)
def update_coach_profile(db: db_dependency, payload: CoachProfileUpdate, current=Depends(require_role(["admin", "coach"]))):

    """Update existing coach profile"""
    return coach_services.create_or_update_profile(db, current.id, payload)



@router.put("/me/availability", response_model=CoachProfileOut, status_code=status.HTTP_200_OK)
def set_availability(db: db_dependency, available: bool = Query(..., description="Set availability true/false"), current=Depends(require_role(["admin", "coach"]))):

    """Set coach availability"""
    return coach_services.set_availability(db, current.id, available)



@router.post("/me/photo", response_model=CoachMeOut)
async def upload_coach_photo(db: db_dependency, file: UploadFile = File(...), current=Depends(require_role(["admin", "coach"]))):

    """Upload/replace coach profile photo"""
    if not isinstance(current, Users):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid current user object.")
        
    rel_path = await save_profile_photo(file, user_id = current.id)
    updated_user = user_services.update_me(db, current.id, UserProfileUpdate(profile_photo=rel_path))
    return updated_user



# ----------------------
# Coach Slot Endpoints
# ----------------------


# Create Slot (Coach)
@router.post("/me/slots", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
def create_slot(db: db_dependency, payload: CoachSlotCreate, current=Depends(require_role(["coach"]))):
    slot = coach_services.create_coach_slot(db, current.id, payload)
    return coach_services.format_slot_for_public(slot)



# List Current Coach Slots
@router.get("/me/slots", response_model=List[CoachSlotResponse], status_code=status.HTTP_200_OK)
def list_current_coach_slots(db: db_dependency, current=Depends(require_role(["coach"]))):
    slots = coach_services.get_slots_by_coach(db, current.id)
    return [coach_services.format_slot_for_me(slot) for slot in slots]



# Update Coach Slot
@router.put("/me/slots/{slot_id}", response_model=SlotOut)
def update_slot(db: db_dependency, slot_id: int, payload: CoachSlotUpdate, current=Depends(require_role(["coach"]))):
    slot = coach_services.update_coach_slot(db, slot_id, current.id, payload)
    return coach_services.format_slot_for_public(slot)



# Delete Coach Slot
@router.delete("/me/slots/{slot_id}", status_code=status.HTTP_200_OK)
def delete_slot(db: db_dependency, slot_id: int, current=Depends(require_role(["coach"]))):
    return coach_services.delete_slot(db, current.id, slot_id)



# ----------------------
# Public Coach Endpoints
# ----------------------


@router.get("/", response_model=List[CoachBrowseOut], status_code=status.HTTP_200_OK)
def browse_coaches(
    db: db_dependency, 
    specialization: Optional[str] = Query(None, description="Filter by specialization"), 
    available_only: bool = Query(False, description="Only show available coaches")
    ):
    """Publicly browse or search coaches with filters"""
    return coach_services.browse_coaches(db, specialization, available_only)



@router.get("/{coach_id}", response_model=CoachBrowseOut)
def get_coach_with_slots_route(db: db_dependency, coach_id: int):
    """Get a coach with profile and their available slots"""
    coach = coach_services.get_coach_with_slots(db, coach_id)

    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")

    # if hasattr(coach, "slots"):
    coach.available_slots = [coach_services.format_slot_for_public(slot) for slot in coach.slots]

    return coach



# ----------------------
# Admin Endpoints
# ----------------------


@router.get("/admin/list", response_model=List[CoachMeOut])
def admin_list_profiles(db: db_dependency, role: Optional[str] = Query(None), current=Depends(require_role(["admin"]))):
    """Admin: list all users, optionally filter by role"""
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this resource.")
    return coach_services.admin_list_profiles(db, role)