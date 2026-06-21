from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.staff import Staff
from ..models.student import Student
from ..models.enums import StaffRole
from ..core.security import hash_password, verify_password


def authenticate_staff(db: Session, username: str, password: str) -> Staff | None:
    """Authenticate a staff member (teacher or admin)"""
    user = db.query(Staff).filter(Staff.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def authenticate_student(db: Session, username: str, password: str) -> Student | None:
    """Authenticate a student"""
    user = db.query(Student).filter(Student.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_staff_by_id(db: Session, user_id: int) -> Staff | None:
    return db.query(Staff).filter(Staff.id == user_id).first()


def get_student_by_id(db: Session, user_id: int) -> Student | None:
    return db.query(Student).filter(Student.id == user_id).first()


def create_staff(
    db: Session, username: str, password: str, name: str, role: str, subject: str | None = None, gender: str | None = None
) -> Staff:
    kwargs: dict = {
        "username": username,
        "password_hash": hash_password(password),
        "password_plain": password,
        "name": name,
        "role": role,
    }
    if subject:
        kwargs["subject"] = subject
    if gender:
        kwargs["gender"] = gender
    user = Staff(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_student(
    db: Session, username: str, password: str, name: str,
    gender: str | None = None, class_id: int | None = None
) -> Student:
    kwargs: dict = {
        "username": username,
        "password_hash": hash_password(password),
        "password_plain": password,
        "name": name,
    }
    if gender:
        kwargs["gender"] = gender
    if class_id:
        kwargs["class_id"] = class_id
    user = Student(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def init_admin(db: Session):
    """Create default admin if not exists"""
    admin = db.query(Staff).filter(Staff.username == "admin").first()
    if not admin:
        create_staff(db, "admin", "admin123", "系统管理员", "admin")
    else:
        if not admin.password_plain:
            admin.password_plain = "admin123"
            db.commit()
