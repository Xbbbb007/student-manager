"""错题本管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from ..database import get_db
from ..models.mistake import Mistake
from ..models.student import Student
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.teacher_class import TeacherClass
from ..models.enums import StaffRole, Subject
from ..schemas.mistake import (
    MistakeCreate,
    MistakeResponse,
    MistakeStatsResponse,
    MistakeSubjectStat,
)
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/mistakes", tags=["错题本"])

SUBJECT_MAP = {
    "chinese": "语文", "math": "数学", "english": "英语",
    "science": "科学", "ethics": "道德与法治",
}


def get_current_staff(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Staff:
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
    user = get_staff_by_id(db, int(payload.get("sub", 0)))
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


def get_current_student(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Student:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    user_type = payload.get("user_type")
    if user_type != "student":
        raise HTTPException(403, detail="仅学生可执行此操作")
    user = db.query(Student).filter(Student.id == int(payload.get("sub", 0))).first()
    if not user:
        raise HTTPException(404, detail="学生不存在")
    return user


# --- 学生端接口 ---

@router.get("/my")
def get_my_mistakes(
    is_mastered: Optional[bool] = None,
    subject: Optional[str] = None,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：查询自己的错题列表"""
    query = db.query(Mistake).filter(Mistake.student_id == current_user.id)
    
    if is_mastered is not None:
        query = query.filter(Mistake.is_mastered == is_mastered)
    if subject:
        query = query.filter(Mistake.subject == subject)

    mistakes = query.order_by(Mistake.created_at.desc()).all()

    data = []
    for m in mistakes:
        data.append({
            "id": m.id,
            "student_id": m.student_id,
            "subject": m.subject,
            "subject_name": SUBJECT_MAP.get(m.subject, m.subject),
            "exam_id": m.exam_id,
            "test_id": m.test_id,
            "question_desc": m.question_desc,
            "my_answer": m.my_answer,
            "correct_answer": m.correct_answer,
            "is_mastered": m.is_mastered,
            "created_at": m.created_at,
        })
    return ApiResponse(data=data)


@router.post("/add")
def add_mistake(
    body: MistakeCreate,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：手动录入错题"""
    m = Mistake(
        student_id=current_user.id,
        subject=body.subject,
        question_desc=body.question_desc,
        my_answer=body.my_answer,
        correct_answer=body.correct_answer,
        exam_id=body.exam_id,
        test_id=body.test_id,
        is_mastered=False,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return ApiResponse(message="录入错题成功", data={"id": m.id})


@router.put("/master/{mistake_id}")
def toggle_mistake_mastered(
    mistake_id: int,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：标记掌握/取消掌握状态切换"""
    m = db.query(Mistake).filter(Mistake.id == mistake_id).first()
    if not m:
        raise HTTPException(404, detail="错题不存在")
    if m.student_id != current_user.id:
        raise HTTPException(403, detail="无权操作")

    m.is_mastered = not m.is_mastered
    db.commit()
    return ApiResponse(message="修改成功", data={"is_mastered": m.is_mastered})


@router.get("/stats")
def get_mistake_stats(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：获取错题本统计看板"""
    total = db.query(Mistake).filter(Mistake.student_id == current_user.id).count()
    mastered = db.query(Mistake).filter(
        Mistake.student_id == current_user.id,
        Mistake.is_mastered == True
    ).count()

    active = total - mastered
    mastered_rate = (mastered / total * 100) if total > 0 else 0.0

    by_subj = []
    for s_key, s_name in SUBJECT_MAP.items():
        sub_total = db.query(Mistake).filter(
            Mistake.student_id == current_user.id,
            Mistake.subject == s_key
        ).count()
        sub_mastered = db.query(Mistake).filter(
            Mistake.student_id == current_user.id,
            Mistake.subject == s_key,
            Mistake.is_mastered == True
        ).count()

        by_subj.append({
            "subject": s_key,
            "subject_name": s_name,
            "count": sub_total,
            "mastered_count": sub_mastered
        })

    return ApiResponse(data={
        "total": total,
        "mastered": mastered,
        "active": active,
        "mastered_rate": round(mastered_rate, 1),
        "by_subject": by_subj
    })


# --- 教师端接口 ---

@router.get("/teacher/class-stats")
def get_teacher_class_mistake_stats(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端/班主任：获取全班或授课班级的错题分布与高频高错学生排行"""
    if current_user.role == StaffRole.ADMIN:
        classes = db.query(Class).all()
    else:
        # Find classes taught
        homeroom_classes = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).all()
        tcs = (
            db.query(Class)
            .join(TeacherClass, Class.id == TeacherClass.class_id)
            .filter(TeacherClass.teacher_id == current_user.id)
            .all()
        )
        classes = list({c for c in (homeroom_classes + tcs)})

    if not classes:
        return ApiResponse(data=[])

    data = []
    for cls in classes:
        # Get students in class
        students = db.query(Student).filter(Student.class_id == cls.id).all()
        student_ids = [s.id for s in students]

        if not student_ids:
            continue

        # Filter subject (if not admin, check teacher subject)
        subj_filter = current_user.subject
        
        # Calculate totals
        query = db.query(Mistake).filter(Mistake.student_id.in_(student_ids))
        if current_user.role != StaffRole.ADMIN and subj_filter:
            query = query.filter(Mistake.subject == subj_filter)

        total_mistakes = query.count()

        # Top students with mistakes
        top_students_raw = (
            db.query(Student.name, func.count(Mistake.id).label("cnt"))
            .join(Mistake, Student.id == Mistake.student_id)
            .filter(Student.class_id == cls.id)
        )
        if current_user.role != StaffRole.ADMIN and subj_filter:
            top_students_raw = top_students_raw.filter(Mistake.subject == subj_filter)

        top_students = (
            top_students_raw.group_by(Student.id)
            .order_by(func.count(Mistake.id).desc())
            .limit(5)
            .all()
        )

        data.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "total_mistakes": total_mistakes,
            "top_students": [
                {"name": name, "mistake_count": cnt} for name, cnt in top_students
            ]
        })

    return ApiResponse(data=data)


# --- 管理端接口 ---

@router.get("/admin/trends")
def get_admin_mistake_trends(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理员端：获取全校错题的学科分布趋势"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="无管理员权限")

    # Get mistake counts by subject
    results = (
        db.query(Mistake.subject, func.count(Mistake.id))
        .group_by(Mistake.subject)
        .all()
    )

    data = []
    for subj_key, cnt in results:
        data.append({
            "subject": subj_key,
            "subject_name": SUBJECT_MAP.get(subj_key, subj_key),
            "count": cnt
        })

    return ApiResponse(data=data)
