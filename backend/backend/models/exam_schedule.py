from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum
from ..database import Base
from .enums import Subject


class ExamSchedule(Base):
    """考试安排表"""

    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject = Column(
        SAEnum(Subject, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    exam_date = Column(Date, nullable=False)
    start_time = Column(String(50), nullable=False)  # "09:00"
    end_time = Column(String(50), nullable=False)    # "11:30"
    location = Column(String(100), nullable=False)   # "教学楼三楼301"
    status = Column(String(20), nullable=False, default="未开始")  # 未开始, 进行中, 已结束
