from sqlalchemy import Column, Integer, String, Enum as SAEnum
from ..database import Base
from .enums import StaffRole, Gender, Subject


class Staff(Base):
    """教职工表 — 教师和管理员"""

    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    password_plain = Column(String(128), default="")
    name = Column(String(50), nullable=False)
    role = Column(
        SAEnum(StaffRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StaffRole.TEACHER,
    )
    gender = Column(
        SAEnum(Gender, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    subject = Column(
        SAEnum(Subject, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
