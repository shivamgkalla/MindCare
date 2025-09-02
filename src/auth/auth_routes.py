from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from . import auth_models
from src.database import get_db
from src.auth import auth_services, auth_schemas
from src.auth.auth_services import create_user, get_current_user, send_forgot_password_email, reset_user_password, verify_user_email, resend_verification_email
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.auth_schemas import CreateUserRequest, UserResponse, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, ResendVerificationRequest



router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)


db_dependency = Annotated[Session, Depends(get_db)]



@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    return create_user(db, create_user_request)



@router.post("/verify-email")
def verify_email(db: db_dependency, token: str):
    user, message = verify_user_email(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"message": message}



@router.post("/resend-verification")
def resend_verification(request: ResendVerificationRequest, db: db_dependency):
    return resend_verification_email(db, request.email)



@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_user(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    return auth_services.login_user(db, form_data.username, form_data.password)



@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_me(current_user: Annotated[auth_models.Users, Depends(get_current_user)]):
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted.")
    return current_user



@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: auth_schemas.ForgotPasswordRequest, db: db_dependency):
    message = send_forgot_password_email(db, request.email)

    return {"message": message}



@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: db_dependency):
    user, message = reset_user_password(db, request.token, request.new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"message": message}