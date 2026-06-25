"""作业管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models.homework import Homework, HomeworkSubmission
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.student import Student
from ..models.enums import StaffRole
from ..schemas.homework import (
    HomeworkCreate,
    HomeworkResponse,
    HomeworkSubmissionCreate,
    HomeworkSubmissionResponse,
    HomeworkGradeRequest,
)
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/homework", tags=["作业管理"])


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
def get_my_homework(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：获取本班级所有作业，附带提交状态"""
    if not current_user.class_id:
        return ApiResponse(data=[])

    homeworks = (
        db.query(Homework)
        .filter(Homework.class_id == current_user.class_id)
        .order_by(Homework.due_date.desc())
        .all()
    )

    data = []
    for hw in homeworks:
        # Check if student submitted this homework
        sub = (
            db.query(HomeworkSubmission)
            .filter(
                HomeworkSubmission.homework_id == hw.id,
                HomeworkSubmission.student_id == current_user.id,
            )
            .first()
        )

        teacher = db.query(Staff).filter(Staff.id == hw.teacher_id).first()
        cls = db.query(Class).filter(Class.id == hw.class_id).first()

        data.append({
            "id": hw.id,
            "title": hw.title,
            "description": hw.description,
            "subject": hw.subject,
            "class_id": hw.class_id,
            "class_name": cls.name if cls else "",
            "teacher_id": hw.teacher_id,
            "teacher_name": teacher.name if teacher else "",
            "due_date": hw.due_date,
            "created_at": hw.created_at,
            "status": sub.status if sub else "unsubmitted",
            "grade": sub.grade if sub else None,
            "feedback": sub.feedback if sub else None,
            "submission_id": sub.id if sub else None,
            "submission_content": sub.content if sub else None,
            "submitted_at": sub.submitted_at if sub else None,
        })

    return ApiResponse(data=data)


@router.post("/submit/{homework_id}")
def submit_homework(
    homework_id: int,
    body: HomeworkSubmissionCreate,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：提交作业"""
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(404, detail="作业不存在")

    # Check if student belongs to the homework's class
    if hw.class_id != current_user.class_id:
        raise HTTPException(403, detail="无权提交此作业")

    # Check if already submitted
    sub = (
        db.query(HomeworkSubmission)
        .filter(
            HomeworkSubmission.homework_id == homework_id,
            HomeworkSubmission.student_id == current_user.id,
        )
        .first()
    )

    if sub:
        # Overwrite submission content
        sub.content = body.content
        sub.submitted_at = func.now()
        # If it was already graded, reset status to submitted
        sub.status = "submitted"
        sub.grade = None
        sub.feedback = None
    else:
        sub = HomeworkSubmission(
            homework_id=homework_id,
            student_id=current_user.id,
            content=body.content,
            status="submitted",
        )
        db.add(sub)

    db.commit()
    db.refresh(sub)
    return ApiResponse(message="作业提交成功", data={"id": sub.id})


# --- 教师端接口 ---

@router.post("/create")
def create_homework(
    body: HomeworkCreate,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：布置作业"""
    if current_user.role not in [StaffRole.ADMIN, StaffRole.TEACHER]:
        raise HTTPException(403, detail="仅教师/管理员有权限布置作业")

    # If teacher is not admin, check subject match
    if current_user.role == StaffRole.TEACHER and current_user.subject != body.subject:
        # Check homeroom teacher permissions
        # If class's homeroom teacher, allowed for all subjects
        cls = db.query(Class).filter(Class.id == body.class_id).first()
        if not cls or cls.homeroom_teacher_id != current_user.id:
            raise HTTPException(403, detail="不能布置非授课科目的作业")

    hw = Homework(
        title=body.title,
        description=body.description,
        subject=body.subject,
        class_id=body.class_id,
        teacher_id=current_user.id,
        due_date=body.due_date,
    )
    db.add(hw)
    db.commit()
    db.refresh(hw)

    return ApiResponse(message="作业布置成功", data={"id": hw.id})


@router.get("/teacher/list")
def get_teacher_homeworks(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：获取自己布置的作业列表"""
    # Admins get all homeworks; teachers get their own
    query = db.query(Homework)
    if current_user.role != StaffRole.ADMIN:
        query = query.filter(Homework.teacher_id == current_user.id)

    homeworks = query.order_by(Homework.created_at.desc()).all()

    data = []
    for hw in homeworks:
        cls = db.query(Class).filter(Class.id == hw.class_id).first()
        teacher = db.query(Staff).filter(Staff.id == hw.teacher_id).first()

        # Count submissions
        total_students = db.query(Student).filter(Student.class_id == hw.class_id).count()
        sub_count = db.query(HomeworkSubmission).filter(HomeworkSubmission.homework_id == hw.id).count()
        graded_count = (
            db.query(HomeworkSubmission)
            .filter(
                HomeworkSubmission.homework_id == hw.id,
                HomeworkSubmission.status == "graded",
            )
            .count()
        )

        data.append({
            "id": hw.id,
            "title": hw.title,
            "description": hw.description,
            "subject": hw.subject,
            "class_id": hw.class_id,
            "class_name": cls.name if cls else "",
            "teacher_id": hw.teacher_id,
            "teacher_name": teacher.name if teacher else "",
            "due_date": hw.due_date,
            "created_at": hw.created_at,
            "total_students": total_students,
            "submitted_count": sub_count,
            "graded_count": graded_count,
        })

    return ApiResponse(data=data)


@router.get("/{homework_id}/submissions")
def get_homework_submissions(
    homework_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：获取某次作业的所有提交详情（包括未提交学生名单）"""
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(404, detail="作业不存在")

    # Verify authorization
    if current_user.role != StaffRole.ADMIN and hw.teacher_id != current_user.id:
        # Check if homeroom teacher
        cls = db.query(Class).filter(Class.id == hw.class_id).first()
        if not cls or cls.homeroom_teacher_id != current_user.id:
            raise HTTPException(403, detail="无权查看此班级的作业提交")

    # Get all students in the class
    students = db.query(Student).filter(Student.class_id == hw.class_id).order_by(Student.username.asc()).all()

    # Get all submissions for this homework
    submissions = {
        sub.student_id: sub
        for sub in db.query(HomeworkSubmission).filter(HomeworkSubmission.homework_id == homework_id).all()
    }

    data = []
    for s in students:
        sub = submissions.get(s.id)
        data.append({
            "student_id": s.id,
            "student_name": s.name,
            "student_username": s.username,
            "submission_id": sub.id if sub else None,
            "content": sub.content if sub else None,
            "submitted_at": sub.submitted_at if sub else None,
            "grade": sub.grade if sub else None,
            "feedback": sub.feedback if sub else None,
            "status": sub.status if sub else "unsubmitted",
        })

    return ApiResponse(data=data)


@router.put("/submission/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    body: HomeworkGradeRequest,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：批改并打分"""
    sub = db.query(HomeworkSubmission).filter(HomeworkSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, detail="提交不存在")

    hw = db.query(Homework).filter(Homework.id == sub.homework_id).first()
    if not hw:
        raise HTTPException(404, detail="对应的作业不存在")

    # Check permission
    if current_user.role != StaffRole.ADMIN and hw.teacher_id != current_user.id:
        cls = db.query(Class).filter(Class.id == hw.class_id).first()
        if not cls or cls.homeroom_teacher_id != current_user.id:
            raise HTTPException(403, detail="无权批改此作业")

    sub.grade = body.grade
    sub.feedback = body.feedback
    sub.status = "graded"

    db.commit()
    db.refresh(sub)
    return ApiResponse(message="批改成功", data={"id": sub.id, "status": sub.status})


# --- 管理员 / 班主任端接口 ---

@router.get("/admin/overview")
def get_homework_overview(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """获取所有班级的作业布置量和提交率概览 (管理员或班主任可用)"""
    # If not admin and not homeroom teacher, block
    classes = []
    if current_user.role == StaffRole.ADMIN:
        classes = db.query(Class).all()
    else:
        # Check if homeroom teacher
        classes = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).all()
        if not classes:
            raise HTTPException(403, detail="仅班主任或管理员可查看此概览")

    data = []
    for cls in classes:
        homeworks = db.query(Homework).filter(Homework.class_id == cls.id).all()
        total_students = db.query(Student).filter(Student.class_id == cls.id).count()

        for hw in homeworks:
            sub_count = db.query(HomeworkSubmission).filter(HomeworkSubmission.homework_id == hw.id).count()
            sub_rate = (sub_count / total_students * 100) if total_students > 0 else 0.0

            # Calculate average grade
            avg_grade = db.query(func.avg(HomeworkSubmission.grade)).filter(
                HomeworkSubmission.homework_id == hw.id,
                HomeworkSubmission.status == "graded",
            ).scalar()

            teacher = db.query(Staff).filter(Staff.id == hw.teacher_id).first()

            data.append({
                "homework_id": hw.id,
                "title": hw.title,
                "subject": hw.subject,
                "class_id": cls.id,
                "class_name": cls.name,
                "teacher_name": teacher.name if teacher else "",
                "total_students": total_students,
                "submitted_count": sub_count,
                "submission_rate": round(sub_rate, 2),
                "average_grade": round(float(avg_grade), 2) if avg_grade is not None else None,
                "due_date": hw.due_date,
                "created_at": hw.created_at,
            })

    return ApiResponse(data=data)
