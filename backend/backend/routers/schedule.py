"""课表管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..models.schedule import Schedule
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.student import Student
from ..models.enums import StaffRole
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

SUBJECT_MAP = {
    "chinese": "语文", "math": "数学", "english": "英语",
    "science": "科学", "ethics": "道德与法治", "pe": "体育",
    "music": "音乐", "art": "美术", "it": "信息科技", "self_study": "自习",
}

router = APIRouter(prefix="/api/v1/schedule", tags=["课表管理"])


def get_current_staff(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Staff:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    if payload.get("user_type", "staff") != "staff":
        raise HTTPException(403, detail="仅教职工可操作")
    user = get_staff_by_id(db, int(payload.get("sub", 0)))
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


def get_current_student(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Student:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    if payload.get("user_type") != "student":
        raise HTTPException(403, detail="仅学生可操作")
    user = db.query(Student).filter(Student.id == int(payload.get("sub", 0))).first()
    if not user:
        raise HTTPException(404, detail="学生不存在")
    return user


def _get_teacher_name(db: Session, teacher_id: Optional[int]) -> str:
    if not teacher_id:
        return ""
    t = db.query(Staff).filter(Staff.id == teacher_id).first()
    return t.name if t else ""


@router.get("/my")
def get_my_schedule(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：获取自己的课表"""
    if not current_user.class_id:
        return ApiResponse(data=[])

    schedules = (
        db.query(Schedule)
        .filter(Schedule.class_id == current_user.class_id)
        .order_by(Schedule.day_of_week, Schedule.period)
        .all()
    )

    data = []
    for s in schedules:
        data.append({
            "id": s.id,
            "class_id": s.class_id,
            "day_of_week": s.day_of_week,
            "period": s.period,
            "subject": s.subject,
            "subject_name": SUBJECT_MAP.get(s.subject, s.subject),
            "teacher_name": _get_teacher_name(db, s.teacher_id),
        })

    return ApiResponse(data=data)


@router.get("/class/{class_id}")
def get_class_schedule(
    class_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端/管理端：获取指定班级的课表"""
    schedules = (
        db.query(Schedule)
        .filter(Schedule.class_id == class_id)
        .order_by(Schedule.day_of_week, Schedule.period)
        .all()
    )

    data = []
    for s in schedules:
        data.append({
            "id": s.id,
            "class_id": s.class_id,
            "day_of_week": s.day_of_week,
            "period": s.period,
            "subject": s.subject,
            "subject_name": SUBJECT_MAP.get(s.subject, s.subject),
            "teacher_name": _get_teacher_name(db, s.teacher_id),
        })

    return ApiResponse(data=data)


@router.get("/teacher/{teacher_id}")
def get_teacher_schedule(
    teacher_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：获取某教师的课表（跨班级）"""
    schedules = (
        db.query(Schedule)
        .filter(Schedule.teacher_id == teacher_id)
        .order_by(Schedule.day_of_week, Schedule.period)
        .all()
    )

    data = []
    for s in schedules:
        cls = db.query(Class).filter(Class.id == s.class_id).first()
        data.append({
            "id": s.id,
            "class_id": s.class_id,
            "class_name": cls.name if cls else "",
            "day_of_week": s.day_of_week,
            "period": s.period,
            "subject": s.subject,
            "subject_name": SUBJECT_MAP.get(s.subject, s.subject),
            "teacher_name": _get_teacher_name(db, s.teacher_id),
        })

    return ApiResponse(data=data)


@router.put("/batch")
def batch_update_schedule(
    body: dict,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端/班主任：批量更新课表（先删后插）"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可批量修改课表")

    class_id = body.get("class_id")
    items = body.get("items", [])
    if not class_id:
        raise HTTPException(400, detail="缺少 class_id")

    # 删除该班旧课表
    db.query(Schedule).filter(Schedule.class_id == class_id).delete()

    # 插入新课表
    for item in items:
        s = Schedule(
            class_id=class_id,
            day_of_week=item["day_of_week"],
            period=item["period"],
            subject=item["subject"],
            teacher_id=item.get("teacher_id"),
        )
        db.add(s)

    db.commit()
    return ApiResponse(message="课表更新成功")
