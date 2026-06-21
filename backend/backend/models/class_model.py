from sqlalchemy import Column, Integer, String, ForeignKey
from ..database import Base


class Class(Base):
    """班级表"""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    section = Column(String(20), nullable=False, default="小学部")
    grade = Column(String(20), nullable=False)
    homeroom_teacher_id = Column(
        Integer,
        ForeignKey("staff.id", use_alter=True, name="fk_homeroom"),
        nullable=True,
    )
