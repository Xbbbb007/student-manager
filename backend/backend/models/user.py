from sqlalchemy import Column, Integer, String, Enum as SAEnum, ForeignKey
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Subject(str, enum.Enum):
    CHINESE = "chinese"
    MATH = "math"
    ENGLISH = "english"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    password_plain = Column(String(128), default="")
    name = Column(String(50), nullable=False)
    role = Column(SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.STUDENT)
    gender = Column(SAEnum(Gender, values_callable=lambda x: [e.value for e in x]), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    subject = Column(SAEnum(Subject, values_callable=lambda x: [e.value for e in x]), nullable=True)


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    grade = Column(String(20), nullable=False)
    homeroom_teacher_id = Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_homeroom"), nullable=True)
