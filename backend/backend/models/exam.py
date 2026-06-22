from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from ..database import Base


class Exam(Base):
    """考试表"""

    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    exam_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
