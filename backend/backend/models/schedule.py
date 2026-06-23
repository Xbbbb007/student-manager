"""课表模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from ..database import Base


class Schedule(Base):
    """课表"""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=周一 ~ 5=周五
    period = Column(Integer, nullable=False)  # 1~8
    subject = Column(String(20), nullable=False)
    teacher_id = Column(Integer, ForeignKey("staff.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("class_id", "day_of_week", "period", name="uq_schedule"),
    )
