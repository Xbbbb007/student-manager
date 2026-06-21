from sqlalchemy import Column, Integer, String, Enum as SAEnum, ForeignKey
from ..database import Base
from .enums import Gender


class Student(Base):
    """学生表 — 学生身份信息"""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    password_plain = Column(String(128), default="")
    name = Column(String(50), nullable=False)
    gender = Column(
        SAEnum(Gender, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
