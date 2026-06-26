from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False)  # chinese, math, etc.
    question_type = Column(String(50), nullable=False)  # single, multiple, blank, essay
    question_desc = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)

    creator = relationship("Staff")

class ExamPaper(Base):
    __tablename__ = "exam_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    subject = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    questions = Column(JSON, nullable=False)  # List of question IDs: [1, 3, 5]
    created_by = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    creator = relationship("Staff")

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    subject = Column(String(50), nullable=False)
    grade = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    upload_by = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    uploader = relationship("Staff")
