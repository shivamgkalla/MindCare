from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from src.database import Base



class CoachProfile(Base):
    __tablename__ = "coach_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    qualifications = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    charges_per_slot = Column(Numeric(10,2), nullable=True)
    availability_status = Column(Boolean, default=True)

    user = relationship("Users", back_populates="coach_profile")