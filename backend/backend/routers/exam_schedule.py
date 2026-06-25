"""在线测试管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date
import random

from ..database import get_db
from ..models.exam_schedule import ExamSchedule
from ..models.test_submission import TestSubmission
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.student import Student
from ..models.teacher_class import TeacherClass
from ..models.enums import StaffRole
from ..schemas.exam_schedule import ExamScheduleCreate, ExamScheduleResponse
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/exams-schedule", tags=["测试管理"])

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


def _build_response_list(db: Session, items: List[ExamSchedule]) -> List[dict]:
    data = []
    for s in items:
        class_obj = db.query(Class).filter(Class.id == s.class_id).first()
        
        # Calculate average score for graded submissions
        avg_score = db.query(func.avg(TestSubmission.score)).filter(
            TestSubmission.schedule_id == s.id,
            TestSubmission.status == "graded"
        ).scalar()

        # Count submissions
        total_students = db.query(Student).filter(Student.class_id == s.class_id).count()
        sub_count = db.query(TestSubmission).filter(TestSubmission.schedule_id == s.id).count()

        data.append({
            "id": s.id,
            "name": s.name,
            "class_id": s.class_id,
            "class_name": class_obj.name if class_obj else "",
            "subject": s.subject,
            "subject_name": SUBJECT_MAP.get(s.subject, s.subject),
            "exam_date": s.exam_date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "location": s.location,
            "status": s.status,
            "average_score": round(float(avg_score), 1) if avg_score is not None else None,
            "submitted_count": sub_count,
            "total_students": total_students,
        })
    return data


# --- 学生端接口 ---

@router.get("/my")
def get_my_exam_schedules(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：获取本班的所有测试安排（带自己的测试成绩与作答）"""
    if not current_user.class_id:
        return ApiResponse(data=[])

    schedules = (
        db.query(ExamSchedule)
        .filter(ExamSchedule.class_id == current_user.class_id)
        .order_by(ExamSchedule.exam_date.desc(), ExamSchedule.start_time.asc())
        .all()
    )

    data = []
    for s in schedules:
        class_obj = db.query(Class).filter(Class.id == s.class_id).first()
        
        # Get student's submission for this test
        sub = (
            db.query(TestSubmission)
            .filter(
                TestSubmission.schedule_id == s.id,
                TestSubmission.student_id == current_user.id,
            )
            .first()
        )

        data.append({
            "id": s.id,
            "name": s.name,
            "class_id": s.class_id,
            "class_name": class_obj.name if class_obj else "",
            "subject": s.subject,
            "subject_name": SUBJECT_MAP.get(s.subject, s.subject),
            "exam_date": s.exam_date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "location": s.location,
            "status": s.status,
            "score": sub.score if sub else None,
            "answers": sub.answers if sub else None,
            "submission_status": sub.status if sub else "unsubmitted",
        })

    return ApiResponse(data=data)


@router.post("/submit-test/{schedule_id}")
def student_submit_test(
    schedule_id: int,
    body: dict,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生端：提交测试作答内容"""
    s = db.query(ExamSchedule).filter(ExamSchedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, detail="测试安排不存在")

    sub = (
        db.query(TestSubmission)
        .filter(
            TestSubmission.schedule_id == schedule_id,
            TestSubmission.student_id == current_user.id,
        )
        .first()
    )

    answers = body.get("answers", "")

    if sub:
        sub.answers = answers
        sub.submitted_at = func.now()
        sub.status = "submitted"
    else:
        sub = TestSubmission(
            schedule_id=schedule_id,
            student_id=current_user.id,
            answers=answers,
            status="submitted",
        )
        db.add(sub)

    db.commit()
    return ApiResponse(message="作答提交成功")


# --- 教师端/通用接口 ---

@router.get("/teacher/list")
def get_teacher_exam_schedules(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """教师端：获取相关班级的测试日程（班主任获取本班，科任老师获取授课班级，管理员获取全部）"""
    if current_user.role == StaffRole.ADMIN:
        schedules = db.query(ExamSchedule).order_by(ExamSchedule.exam_date.desc()).all()
        return ApiResponse(data=_build_response_list(db, schedules))

    # Find teacher's classes
    homeroom_classes = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).all()
    tcs = (
        db.query(Class)
        .join(TeacherClass, Class.id == TeacherClass.class_id)
        .filter(TeacherClass.teacher_id == current_user.id)
        .all()
    )
    class_ids = list({c.id for c in (homeroom_classes + tcs)})

    if not class_ids:
        return ApiResponse(data=[])

    schedules = (
        db.query(ExamSchedule)
        .filter(ExamSchedule.class_id.in_(class_ids))
        .order_by(ExamSchedule.exam_date.desc())
        .all()
    )
    return ApiResponse(data=_build_response_list(db, schedules))


@router.post("/create")
def create_exam_schedule(
    body: ExamScheduleCreate,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """发布测试安排（教师或管理员）"""
    if current_user.role not in [StaffRole.ADMIN, StaffRole.TEACHER]:
        raise HTTPException(403, detail="仅教师/管理员有权限发布测试安排")

    class_obj = db.query(Class).filter(Class.id == body.class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")

    schedule = ExamSchedule(
        name=body.name,
        class_id=body.class_id,
        subject=body.subject,
        exam_date=body.exam_date,
        start_time=body.start_time,
        end_time=body.end_time,
        location=body.location,
        status=body.status or "未开始",
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return ApiResponse(message="测试发布成功", data={"id": schedule.id})


@router.put("/update/{schedule_id}")
def update_exam_schedule(
    schedule_id: int,
    body: ExamScheduleCreate,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """修改测试安排"""
    schedule = db.query(ExamSchedule).filter(ExamSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, detail="测试日程不存在")

    if current_user.role not in [StaffRole.ADMIN, StaffRole.TEACHER]:
        raise HTTPException(403, detail="无权操作")

    schedule.name = body.name
    schedule.class_id = body.class_id
    schedule.subject = body.subject
    schedule.exam_date = body.exam_date
    schedule.start_time = body.start_time
    schedule.end_time = body.end_time
    schedule.location = body.location
    schedule.status = body.status or "未开始"

    db.commit()
    return ApiResponse(message="测试安排更新成功")


@router.delete("/delete/{schedule_id}")
def delete_exam_schedule(
    schedule_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """删除测试安排"""
    schedule = db.query(ExamSchedule).filter(ExamSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, detail="测试安排不存在")

    if current_user.role not in [StaffRole.ADMIN, StaffRole.TEACHER]:
        raise HTTPException(403, detail="无权操作")

    # Delete related submissions first
    db.query(TestSubmission).filter(TestSubmission.schedule_id == schedule_id).delete()

    db.delete(schedule)
    db.commit()
    return ApiResponse(message="测试已删除")


@router.get("/{schedule_id}/submissions")
def get_test_submissions(
    schedule_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """获取某次小测的全班成绩列表"""
    s = db.query(ExamSchedule).filter(ExamSchedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, detail="小测不存在")

    students = db.query(Student).filter(Student.class_id == s.class_id).order_by(Student.username.asc()).all()
    submissions = {
        sub.student_id: sub
        for sub in db.query(TestSubmission).filter(TestSubmission.schedule_id == schedule_id).all()
    }

    data = []
    for st in students:
        sub = submissions.get(st.id)
        data.append({
            "student_id": st.id,
            "student_name": st.name,
            "student_username": st.username,
            "score": sub.score if sub else None,
            "answers": sub.answers if sub else None,
            "status": sub.status if sub else "unsubmitted",
        })
    return ApiResponse(data=data)


@router.post("/auto-grade/{schedule_id}")
def teacher_auto_grade(
    schedule_id: int,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """一键自动给全班学生进行评分并出具模拟成绩（演示极其方便）"""
    s = db.query(ExamSchedule).filter(ExamSchedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, detail="小测不存在")

    # Get all students in this class
    students = db.query(Student).filter(Student.class_id == s.class_id).all()

    for student in students:
        sub = (
            db.query(TestSubmission)
            .filter(
                TestSubmission.schedule_id == schedule_id,
                TestSubmission.student_id == student.id,
            )
            .first()
        )

        simulated_score = round(random.uniform(70.0, 99.5), 1)
        simulated_answers = f"【系统模拟作答】本次针对「{s.name}」的作答已经顺利上传，自动匹配并给出了高拟真分值。"

        if sub:
            sub.score = simulated_score
            sub.answers = sub.answers or simulated_answers
            sub.status = "graded"
        else:
            sub = TestSubmission(
                schedule_id=schedule_id,
                student_id=student.id,
                score=simulated_score,
                answers=simulated_answers,
                status="graded",
            )
            db.add(sub)

    s.status = "已结束"
    db.commit()
    return ApiResponse(message="已一键对全班自动打分完成！")


# --- 管理端专用接口 ---

@router.get("/admin/list")
def get_admin_exam_schedules(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：获取全校所有测试列表"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="无管理员权限")

    schedules = db.query(ExamSchedule).order_by(ExamSchedule.exam_date.desc()).all()
    return ApiResponse(data=_build_response_list(db, schedules))


@router.post("/admin/batch")
def batch_create_exam_schedules(
    body: dict,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：批量发布测试日程（多选班级一次发布）"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="无管理员权限")

    class_ids = body.get("class_ids", [])
    name = body.get("name")
    subject = body.get("subject")
    exam_date_str = body.get("exam_date")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    location = body.get("location")

    if not all([class_ids, name, subject, exam_date_str, start_time, end_time, location]):
        raise HTTPException(400, detail="缺少必填参数")

    exam_date = date.fromisoformat(exam_date_str)

    created_ids = []
    for cid in class_ids:
        s = ExamSchedule(
            name=name,
            class_id=cid,
            subject=subject,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            status="未开始",
        )
        db.add(s)
        db.flush()
        created_ids.append(s.id)

    db.commit()
    return ApiResponse(message=f"成功批量发布 {len(created_ids)} 个班级的测试日程")


@router.get("/admin/conflicts")
def detect_exam_conflicts(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理端：检测测试日程冲突（同一天同一班级安排了多场小测）"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="无管理员权限")

    all_schedules = db.query(ExamSchedule).all()
    grouped = {}
    for s in all_schedules:
        key = (s.exam_date, s.class_id)
        grouped.setdefault(key, []).append(s)

    conflicts = []
    for (exam_date, class_id), items in grouped.items():
        if len(items) > 1:
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            conflicts.append({
                "date": str(exam_date),
                "class_id": class_id,
                "class_name": class_obj.name if class_obj else "",
                "exams": [
                    {
                        "id": x.id,
                        "name": x.name,
                        "subject": x.subject,
                        "subject_name": SUBJECT_MAP.get(x.subject, x.subject),
                        "start_time": x.start_time,
                        "end_time": x.end_time,
                        "location": x.location,
                    }
                    for x in items
                ]
            })

    return ApiResponse(data=conflicts)
