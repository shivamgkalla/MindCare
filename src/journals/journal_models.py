from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base



class Journal(Base):
    __tablename__ = "journals"


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable = False)
    image_url = Column(String(500), nullable=True)
    mood = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)


    # Relationships
    user = relationship("Users", back_populates="journals") 