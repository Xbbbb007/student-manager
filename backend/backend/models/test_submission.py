from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, func
from ..database import Base


class TestSubmission(Base):
    """测试提交记录表（存放学生的在线小测作答和自动给出的分数）"""

    __tablename__ = "test_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("exam_schedules.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    score = Column(Float, nullable=True)               # 测试得分，例如 85.5
    answers = Column(Text, nullable=True)               # 作答文本
    submitted_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), nullable=False, default="submitted")  # submitted, graded
