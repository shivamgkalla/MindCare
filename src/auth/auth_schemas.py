from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from src.utils.allowed_roles import ALLOWED_ROLES


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str   # "user" or "coach"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


    @field_validator("role")
    def validate_role(cls, value):
        if value not in ALLOWED_ROLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Oops! Sorry. You cannot register yourself as an admin.")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    phone_number: Optional[str]
    is_active: bool
    is_verified : bool


    class Config:
        model_config = {"from_attributes": True}



class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str