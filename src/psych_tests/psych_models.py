from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database import Base



class PsychTest(Base):
    __tablename__ = "psych_tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    questions = relationship("PsychQuestion", back_populates="test", cascade="all, delete-orphan")



class PsychQuestion(Base):
    __tablename__ = "psych_questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("psych_tests.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)


    test = relationship("PsychTest", back_populates="questions")
    options = relationship("PsychOption", back_populates="question", cascade="all, delete-orphan")



class PsychOption(Base):
    __tablename__ = "psych_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("psych_questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)


    question  = relationship("PsychQuestion", back_populates="options")



class PsychUserResponse(Base):
    __tablename__ = "psych_user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_id = Column(Integer, ForeignKey("psych_tests.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("psych_questions.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(Integer, ForeignKey("psych_options.id", ondelete="CASCADE"), nullable=False)