from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from src.database import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class Users(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, nullable=False)   # "user" or "coach"
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    # New profile fields
    age = Column(Integer, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    location = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)

    # Relationships
    coach_profile = relationship("CoachProfile", back_populates="user", uselist=False)
    journals = relationship("Journal", back_populates="user", cascade="all, delete")


    # Slot booking relationships
    user_bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id", cascade="all, delete")
    coach_bookings = relationship("Booking", back_populates="coach", foreign_keys="Booking.coach_id", cascade="all, delete")
    slots = relationship("CoachSlot", back_populates="coach", cascade="all, delete")