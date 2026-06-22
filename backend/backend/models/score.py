from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint, Enum as SAEnum
from ..database import Base
from .enums import Subject


class Score(Base):
    """成绩表"""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    subject = Column(
        SAEnum(Subject, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    score = Column(Float, nullable=False)
    class_rank = Column(Integer, nullable=True)
    school_rank = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "exam_id", "subject", name="uq_score"),
    )
