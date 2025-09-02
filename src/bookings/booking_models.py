from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timezone
from src.database import Base



class BookingStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"



class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint('slot_id', name='uq_booking_slot'), )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column (Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(Integer, ForeignKey("coach_slots.id", ondelete="SET NULL"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.scheduled, nullable=False)
    notes = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False)


    # Relationships
    user = relationship("Users", foreign_keys=[user_id])
    coach = relationship("Users", foreign_keys=[coach_id])
    slot = relationship("CoachSlot", back_populates="bookings")



class CoachSlot(Base):
    __tablename__ = "coach_slots"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    price = Column(Numeric(10,2), nullable=True)  # override per slot if needed
    is_booked = Column(Boolean, default=False)



    # Relationships
    coach = relationship("Users", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete")