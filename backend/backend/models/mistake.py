from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SAEnum, func
from ..database import Base
from .enums import Subject


class Mistake(Base):
    """错题本表"""

    __tablename__ = "mistakes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(
        SAEnum(Subject, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)                  # 可选，关联正式考试
    test_id = Column(Integer, ForeignKey("exam_schedules.id"), nullable=True)          # 可选，关联课堂测试
    question_desc = Column(Text, nullable=False)                                      # 题目描述
    my_answer = Column(Text, nullable=True)                                           # 我的作答
    correct_answer = Column(Text, nullable=True)                                      # 正确解答
    is_mastered = Column(Boolean, nullable=False, default=False)                      # 是否掌握
    created_at = Column(DateTime, server_default=func.now())
