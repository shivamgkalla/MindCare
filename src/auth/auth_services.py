from datetime import datetime, timedelta, timezone
import stat
from typing import Annotated, Optional, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.core.config import settings
from src.core.security import hash_password, create_reset_token, verify_reset_token
from src.core.security import create_email_verification_token, verify_email_verification_token
from src.auth.auth_models import Users
from src.database import get_db
from src.utils.allowed_roles import ALLOWED_ROLES
from src.utils.email_service import send_email


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# OAuth2 scheme (for get_current_user)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username(db: Session, username: str) -> Optional[Users]:
    return db.query(Users).filter(Users.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[Users]:
    return db.query(Users).filter(Users.email == email).first()


def create_user(db: Session, user_data) -> Users:
    if user_data.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid role.")

    
    if get_user_by_username(db, user_data.username) or get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    user = Users(
        email = user_data.email,
        username = user_data.username,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        role = user_data.role,
        phone_number = user_data.phone_number,
        hashed_password = hash_password(user_data.password),
        is_active = True,
        is_verified = False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email
    send_verification_email(db, user)

    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[Users]:
    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    encode = data.copy()
    expires = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    encode.update({"exp": expires})
    encoded_jwt = jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def login_user(db: Session, username: str, password: str) -> dict:
    user = authenticate_user(db, username, password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified. Please check your inbox.")


    access_token = create_access_token(data={"sub": user.username, "id": user.id, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}



async def get_current_user(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]) -> Users:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        
        user = db.query(Users).filter(Users.id == user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")



def require_role(allowed_roles: List[str]):
    allowed_roles_lower = {role.lower() for role in allowed_roles}  # precompute once

    async def role_checker(current_user: Users = Depends(get_current_user)) -> Users:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials.")

        if not current_user.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role not set.")


        if current_user.role.lower() not in allowed_roles_lower:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource.")

        return current_user
    return role_checker



def send_verification_email(db: Session, user: Users):
    token = create_email_verification_token(user.email)
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    subject = "Verify your MindCare Account"
    body = f"Click the link to veirfy your email: {verification_link}"

    send_email(to_email=user.email, subject=subject, body=body)

    return "Verification email sent."


def verify_user_email(db: Session, token: str):
    email = verify_email_verification_token(token)
    if not email:
        return None, "Invalid or expired token"

    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        return None, "User not found"

    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user, "Email verified successfully"


def resend_verification_email(db: Session, email: str):

    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")
    
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")

    send_verification_email(db, user)
    return{"message": "Verification email resent. Please check your inbox."}



def send_forgot_password_email(db: Session, email: str):

    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")

    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first.")

    token  = create_reset_token(user.email)
    reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
    subject = "MindCare Password Reset"
    body = f"Click the link to reset your password: {reset_link}"
    send_email(to_email=user.email, subject=subject, body=body)

    return "A reset link has been sent to your account."


def reset_user_password(db: Session, token: str, new_password: str):

    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN ,detail="Please verify your email first.")
    
    if verify_password(new_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as previous password.")

    hashed = hash_password(new_password)
    user.hashed_password = hashed
    db.commit()
    db.refresh(user)
    return user, "Password has been reset successfully"