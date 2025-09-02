from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from src.auth.auth_models import Users
from src.database import get_db
from src.auth.auth_services import get_current_user, require_role
from src.users.user_schemas import UserProfileMe, UserProfileUpdate
from src.users import user_services
from src.utils.file_upload import save_profile_photo



router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)



db_dependency = Annotated[Session, Depends(get_db)]



@router.get("/me", response_model=UserProfileMe, status_code=status.HTTP_200_OK)
def get_my_profile(db: db_dependency, current_user: Users = Depends(require_role(["admin", "user"]))):
    user_object = user_services.get_me(db, current_user.id)
    if not user_object:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return user_object



@router.put("/me", response_model=UserProfileMe)
def update_my_profile(payload: UserProfileUpdate, db: db_dependency, current_user: Users = Depends(require_role(["user", "admin"]))):
    user_object = user_services.update_me(db, current_user.id, payload)
    return user_object



@router.post("/me/photo", response_model=UserProfileMe, status_code=status.HTTP_200_OK)
async def upload_profile_photo(db: db_dependency, file: UploadFile = File(), current_user: Users = Depends(require_role(["user", "admin"]))):
    rel_path = await save_profile_photo(file, user_id = current_user.id)
    updated = user_services.update_me(db, current_user.id, payload=UserProfileUpdate(profile_photo=rel_path))
    return updated