from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from src.auth.auth_models import Users, GenderEnum
from src.users.user_schemas import UserProfileUpdate



def get_me(db: Session, user_id: int) -> Users:
    user = db.query(Users).filter(Users.id == user_id, Users.role=="user").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or role mismatch")

    return user



def update_me(db: Session, user_id: int, payload: UserProfileUpdate) -> Users:
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Only update the provided fields
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)


    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def admin_get_profile(db: Session, user_id: int) -> Users:
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user



def admin_update_profile(db: Session, user_id: int, payload: UserProfileUpdate) -> Users:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource cannot be modified.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



def admin_delete_profile(db: Session, user_id: int) -> None:
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()