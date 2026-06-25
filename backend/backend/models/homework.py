from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum as SAEnum, func
from ..database import Base
from .enums import Subject


class Homework(Base):
    """作业表"""

    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(
        SAEnum(Subject, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class HomeworkSubmission(Base):
    """作业提交表"""

    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    content = Column(Text, nullable=False)
    submitted_at = Column(DateTime, server_default=func.now())
    grade = Column(Float, nullable=True)  # 分数，例如 95.5
    feedback = Column(Text, nullable=True)         # 批改评语
    status = Column(String(20), nullable=False, default="submitted")  # submitted, graded
