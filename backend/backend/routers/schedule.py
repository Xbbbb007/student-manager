"""课表管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from collections import defaultdict

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
    "music": "音乐", "art": "美术", "it": "信息科技", "self-study": "自习",
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
    """管理端/班主任/科任老师：批量更新课表（先删后插）"""
    class_id = body.get("class_id")
    items = body.get("items", [])
    if not class_id:
        raise HTTPException(400, detail="缺少 class_id")

    # 管理员可以改任何班，教师只能改自己教的班
    if current_user.role != StaffRole.ADMIN:
        teaches = db.query(Schedule).filter(
            Schedule.class_id == class_id,
            Schedule.teacher_id == current_user.id,
        ).first()
        if not teaches:
            raise HTTPException(403, detail="您不教该班级，无法修改课表")

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


@router.get("/admin/overview")
def admin_schedule_overview(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：全校课表概览 — 返回所有班级的课表摘要"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可查看全校课表")

    classes = db.query(Class).order_by(Class.section, Class.grade, Class.name).all()
    result = []
    for cls in classes:
        schedules = db.query(Schedule).filter(Schedule.class_id == cls.id).all()
        periods_count = len(schedules)
        subjects = list(set(s.subject for s in schedules))
        teacher_ids = list(set(s.teacher_id for s in schedules if s.teacher_id))
        result.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "section": cls.section,
            "grade": cls.grade,
            "periods_count": periods_count,
            "subjects": [SUBJECT_MAP.get(s, s) for s in subjects],
            "teacher_count": len(teacher_ids),
        })
    return ApiResponse(data=result)


@router.get("/admin/statistics")
def admin_class_hours_statistics(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：课时统计 — 每位教师每周课时量"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可查看课时统计")

    # 按 teacher_id 分组统计
    rows = (
        db.query(Schedule.teacher_id, func.count(Schedule.id).label("hours"))
        .filter(Schedule.teacher_id.isnot(None))
        .group_by(Schedule.teacher_id)
        .all()
    )
    result = []
    for row in rows:
        teacher = db.query(Staff).filter(Staff.id == row.teacher_id).first()
        if teacher:
            result.append({
                "teacher_id": row.teacher_id,
                "teacher_name": teacher.name,
                "subject": teacher.subject.value if teacher.subject else "",
                "weekly_hours": row.hours,
            })
    result.sort(key=lambda x: x["weekly_hours"], reverse=True)
    return ApiResponse(data=result)


@router.get("/admin/conflicts")
def admin_detect_conflicts(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：冲突检测 — 教师同一时间段被安排了多节课"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可检测冲突")

    # 找出所有教师的课表，按 (teacher_id, day_of_week, period) 分组
    all_schedules = (
        db.query(Schedule)
        .filter(Schedule.teacher_id.isnot(None))
        .order_by(Schedule.teacher_id, Schedule.day_of_week, Schedule.period)
        .all()
    )

    # 按 (teacher_id, day, period) 分组
    groups: dict = defaultdict(list)
    for s in all_schedules:
        key = (s.teacher_id, s.day_of_week, s.period)
        groups[key].append(s)

    conflicts = []
    day_names = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
    for (tid, day, period), items in groups.items():
        if len(items) > 1:
            teacher = db.query(Staff).filter(Staff.id == tid).first()
            class_names = []
            for item in items:
                cls = db.query(Class).filter(Class.id == item.class_id).first()
                class_names.append(cls.name if cls else f"班级{item.class_id}")
            conflicts.append({
                "teacher_id": tid,
                "teacher_name": teacher.name if teacher else "",
                "day_of_week": day,
                "day_name": day_names.get(day, ""),
                "period": period,
                "classes": class_names,
                "description": f"{teacher.name if teacher else ''} 在{day_names.get(day, '')}第{period}节同时被安排了 {', '.join(class_names)} 的课",
            })
    return ApiResponse(data=conflicts)
