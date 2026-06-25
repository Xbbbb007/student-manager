from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from ..database import Base


class TeacherClass(Base):
    """教师-班级关联表"""

    __tablename__ = "teacher_classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("teacher_id", "class_id", "subject", name="uq_teacher_class"),
    )
