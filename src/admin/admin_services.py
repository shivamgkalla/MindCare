from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.auth.auth_models import Users
from src.core.security import hash_password
from src.auth.auth_services import get_user_by_email, get_user_by_username
from src.coaches.coach_models import CoachProfile
from src.admin.admin_schemas import AdminProfileOut, AdminUserCreate, CoachProfileOut, AdminCoachProfileOut
from src.bookings.booking_models import Booking
from src.utils.allowed_roles import ALLOWED_ROLES



def create_user_as_admin(db: Session, user_data: AdminUserCreate) -> AdminProfileOut:
    if user_data.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sorry, you cannot register yourself as admin.")

    if get_user_by_username(db, user_data.username) or get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered.")

    user = Users(
        email = user_data.email,
        username = user_data.username,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        role = user_data.role,
        phone_number = user_data.phone_number,
        hashed_password = hash_password(user_data.password),
        is_active = True,
        is_verified = True  # Admin-created users are auto-verified
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    

    # Attach coach profile if role=coach
    coach_profile = None
    if user.role == "coach":
        coach_profile = CoachProfile(user_id=user.id)
        db.add(coach_profile)
        db.commit()
        db.refresh(coach_profile)

    return AdminProfileOut.model_validate(user, from_attributes=True)



def list_profiles(db: Session, role: Optional[str] = None) -> List[AdminProfileOut]:
    if role and role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role filter")

    query = db.query(Users)
    if role:
        query = query.filter(Users.role == role)
    users = query.all()

    results = []

    for user in users:
        coach_obj = db.query(CoachProfile).filter(CoachProfile.user_id == user.id).first()
        coach_profile = (
            CoachProfileOut.model_validate(
                {key: getattr(coach_obj, key) for key in CoachProfileOut.model_fields}
            )
            if coach_obj else None
        )

        results.append(
            AdminProfileOut.model_validate({
                **{key: getattr(user, key) for key in AdminProfileOut.model_fields if key != "coach_profile"},
                "coach_profile": coach_profile
            })
        )
    return results



def get_profile(db: Session, user_id: int) -> AdminProfileOut:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted.")

    coach_obj = db.query(CoachProfile).filter(CoachProfile.user_id == user_id).first()
    coach_profile = (
        AdminCoachProfileOut.model_validate(
            {key: getattr(coach_obj, key) for key in CoachProfileOut.model_fields}
        )
        if coach_obj else None
    )
    return AdminProfileOut.model_validate({
        **{key: getattr(user, key) for key in AdminProfileOut.model_fields if key != "coach_profile"},
        "coach_profile": coach_profile
    })



def delete_profile(db: Session, user_id: int) -> None:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource cannot be deleted.")
    
    db.delete(user)
    db.commit()



def list_all_bookings(db: Session):
    return db.query(Booking).all()