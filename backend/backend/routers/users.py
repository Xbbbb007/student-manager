from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.staff import Staff
from ..models.student import Student
from ..models.enums import StaffRole, Gender, Subject
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id, get_student_by_id, create_staff, create_student
from ..core.security import decode_access_token, hash_password

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


def get_current_staff(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Staff:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    user_type = payload.get("user_type", "staff")
    if user_type != "staff":
        raise HTTPException(403, detail="仅教职工可执行此操作")
    user_id = int(payload.get("sub", 0))
    user = get_staff_by_id(db, user_id)
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


def require_admin(current_user: Staff = Depends(get_current_staff)):
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可执行此操作")
    return current_user


# ─── Legacy merge (all users) ───────────────────────────────


@router.get("/", response_model=ApiResponse)
def list_users_merged(
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    staff_list = db.query(Staff).all()
    student_list = db.query(Student).all()
    data = []
    for u in staff_list:
        data.append({
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role.value,
            "password_plain": u.password_plain or "",
            "class_id": None,
            "gender": u.gender.value if u.gender else None,
            "subject": u.subject.value if u.subject else None,
            "user_type": "staff",
        })
    for u in student_list:
        data.append({
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": "student",
            "password_plain": u.password_plain or "",
            "class_id": u.class_id,
            "gender": u.gender.value if u.gender else None,
            "subject": None,
            "user_type": "student",
        })
    return ApiResponse(data=data)


# ─── Staff CRUD ─────────────────────────────────────────────


@router.get("/staff", response_model=ApiResponse)
def list_staff(
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    staff_list = db.query(Staff).all()
    data = [
        {
            "id": u.id, "username": u.username, "name": u.name,
            "role": u.role.value,
            "gender": u.gender.value if u.gender else None,
            "subject": u.subject.value if u.subject else None,
            "password_plain": u.password_plain or "",
        }
        for u in staff_list
    ]
    return ApiResponse(data=data)


@router.post("/staff", response_model=ApiResponse)
def create_staff_api(
    body: dict,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    username = body.get("username")
    password = body.get("password")
    name = body.get("name")
    role = body.get("role", "teacher")
    gender = body.get("gender")
    subject = body.get("subject")
    if not all([username, password, name]):
        raise HTTPException(400, detail="缺少必填字段")
    if role not in [e.value for e in StaffRole]:
        raise HTTPException(400, detail="无效角色，仅支持 teacher/admin")
    existing = db.query(Staff).filter(Staff.username == username).first()
    if existing:
        raise HTTPException(400, detail="用户名已存在")
    user = create_staff(db, username, password, name, role, subject, gender)
    return ApiResponse(data={
        "id": user.id, "username": user.username, "name": user.name,
        "role": user.role.value, "password_plain": user.password_plain or "",
    })


@router.put("/staff/{user_id}", response_model=ApiResponse)
def update_staff(
    user_id: int,
    body: dict,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(Staff).filter(Staff.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="用户不存在")
    if "name" in body:
        user.name = body["name"]
    if "gender" in body:
        user.gender = Gender(body["gender"]) if body["gender"] else None
    if "subject" in body:
        user.subject = Subject(body["subject"]) if body["subject"] else None
    if "password" in body and body["password"]:
        user.password_hash = hash_password(body["password"])
        user.password_plain = body["password"]
    db.commit()
    db.refresh(user)
    return ApiResponse(data={
        "id": user.id, "username": user.username, "name": user.name,
        "role": user.role.value, "password_plain": user.password_plain or "",
    })


@router.delete("/staff/{user_id}", response_model=ApiResponse)
def delete_staff(
    user_id: int,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(400, detail="不能删除自己")
    user = db.query(Staff).filter(Staff.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return ApiResponse(message="删除成功")


# ─── Student CRUD ───────────────────────────────────────────


@router.get("/students", response_model=ApiResponse)
def list_students(
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    student_list = db.query(Student).all()
    data = [
        {
            "id": u.id, "username": u.username, "name": u.name,
            "gender": u.gender.value if u.gender else None,
            "class_id": u.class_id,
            "password_plain": u.password_plain or "",
        }
        for u in student_list
    ]
    return ApiResponse(data=data)


@router.post("/students", response_model=ApiResponse)
def create_student_api(
    body: dict,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    username = body.get("username")
    password = body.get("password")
    name = body.get("name")
    gender = body.get("gender")
    class_id = body.get("class_id")
    if not all([username, password, name]):
        raise HTTPException(400, detail="缺少必填字段")
    existing = db.query(Student).filter(Student.username == username).first()
    if existing:
        raise HTTPException(400, detail="用户名已存在")
    user = create_student(db, username, password, name, gender, class_id)
    return ApiResponse(data={
        "id": user.id, "username": user.username, "name": user.name,
        "password_plain": user.password_plain or "",
    })


@router.put("/students/{user_id}", response_model=ApiResponse)
def update_student(
    user_id: int,
    body: dict,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="学生不存在")
    if "name" in body:
        user.name = body["name"] or user.name
    if "gender" in body:
        user.gender = Gender(body["gender"]) if body["gender"] else None
    if "class_id" in body:
        user.class_id = body.get("class_id")
    if "password" in body and body["password"]:
        user.password_hash = hash_password(body["password"])
        user.password_plain = body["password"]
    db.commit()
    db.refresh(user)
    return ApiResponse(data={
        "id": user.id, "username": user.username, "name": user.name,
        "password_plain": user.password_plain or "",
    })


@router.delete("/students/{user_id}", response_model=ApiResponse)
def delete_student(
    user_id: int,
    current_user: Staff = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="学生不存在")
    db.delete(user)
    db.commit()
    return ApiResponse(message="删除成功")

