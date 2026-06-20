from sqlalchemy import Column, Integer, String, Enum as SAEnum
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.STUDENT)
