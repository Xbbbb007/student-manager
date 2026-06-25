"""考勤与请假管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date as date_type

from ..database import get_db
from ..models.attendance import Attendance, LeaveRequest
from ..models.student import Student
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.enums import StaffRole, AttendanceStatus, LeaveStatus
from ..schemas.attendance import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    RollCallRequest,
    AttendanceLogResponse,
)
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/attendance", tags=["考勤与请假"])


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


# ─── 学生端接口 ───────────────────────────────────────────────

@router.get("/my/logs")
def get_my_attendance_logs(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生：查询自己的考勤日志"""
    logs = (
        db.query(Attendance)
        .filter(Attendance.student_id == current_user.id)
        .order_by(Attendance.date.desc(), Attendance.period.desc())
        .all()
    )
    
    # Map class name
    cls = db.query(Class).filter(Class.id == current_user.class_id).first()
    cls_name = cls.name if cls else "未知班级"

    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "student_id": log.student_id,
            "student_name": current_user.name,
            "class_id": log.class_id,
            "class_name": cls_name,
            "date": log.date.strftime("%Y-%m-%d"),
            "period": log.period,
            "status": log.status.value,
            "reason": log.reason,
        })
    return ApiResponse(data=data)


@router.get("/my/stats")
def get_my_attendance_stats(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生：查询自己的考勤统计"""
    logs_query = db.query(Attendance).filter(Attendance.student_id == current_user.id)
    total = logs_query.count()
    present = logs_query.filter(Attendance.status == AttendanceStatus.PRESENT).count()
    tardy = logs_query.filter(Attendance.status == AttendanceStatus.TARDY).count()
    absent = logs_query.filter(Attendance.status == AttendanceStatus.ABSENT).count()
    leave = logs_query.filter(Attendance.status == AttendanceStatus.LEAVE).count()

    attendance_rate = (present / (total - leave) * 100) if (total - leave) > 0 else 100.0
    return ApiResponse(data={
        "total": total,
        "present": present,
        "tardy": tardy,
        "absent": absent,
        "leave": leave,
        "attendance_rate": round(attendance_rate, 1),
    })


@router.get("/my/leaves")
def get_my_leaves(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生：获取请假列表"""
    leaves = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.student_id == current_user.id)
        .order_by(LeaveRequest.start_date.desc())
        .all()
    )
    data = []
    for lv in leaves:
        # Get approver name
        approver_name = None
        if lv.approved_by:
            app_staff = db.query(Staff).filter(Staff.id == lv.approved_by).first()
            if app_staff:
                approver_name = app_staff.name
        
        data.append({
            "id": lv.id,
            "student_id": lv.student_id,
            "student_name": current_user.name,
            "start_date": lv.start_date.strftime("%Y-%m-%d"),
            "end_date": lv.end_date.strftime("%Y-%m-%d"),
            "reason": lv.reason,
            "status": lv.status.value,
            "approved_by": lv.approved_by,
            "approved_by_name": approver_name,
            "feedback": lv.feedback,
        })
    return ApiResponse(data=data)


@router.post("/my/leaves")
def create_my_leave_request(
    body: LeaveRequestCreate,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """学生：在线提交请假单"""
    if body.start_date > body.end_date:
        raise HTTPException(400, detail="开始日期不能晚于结束日期")
    
    lv = LeaveRequest(
        student_id=current_user.id,
        start_date=body.start_date,
        end_date=body.end_date,
        reason=body.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(lv)
    db.commit()
    db.refresh(lv)
    return ApiResponse(message="请假申请已提交，等待班主任审核", data={"id": lv.id})


# ─── 教师端接口 ───────────────────────────────────────────────

@router.get("/teacher/class-logs")
def get_teacher_class_logs(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """班主任：获取班级所有考勤日志记录"""
    # Find homeroom class
    cls = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(403, detail="仅班主任可查看班级考勤日志")
    
    logs = (
        db.query(Attendance)
        .filter(Attendance.class_id == cls.id)
        .order_by(Attendance.date.desc(), Attendance.period.desc())
        .all()
    )

    # Get student name map
    students = db.query(Student).filter(Student.class_id == cls.id).all()
    stu_map = {s.id: s.name for s in students}

    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "student_id": log.student_id,
            "student_name": stu_map.get(log.student_id, "未知学生"),
            "class_id": log.class_id,
            "class_name": cls.name,
            "date": log.date.strftime("%Y-%m-%d"),
            "period": log.period,
            "status": log.status.value,
            "reason": log.reason,
        })
    return ApiResponse(data=data)


@router.post("/teacher/roll-call")
def take_roll_call(
    body: RollCallRequest,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """班主任：执行课堂点名录入"""
    # Verify homeroom
    cls = db.query(Class).filter(Class.id == body.class_id).first()
    if not cls or cls.homeroom_teacher_id != current_user.id:
        raise HTTPException(403, detail="您不是该班级的班主任，无权提交点名数据")
    
    # Delete previous roll-calls for this class, date, period to support updates
    db.query(Attendance).filter(
        Attendance.class_id == body.class_id,
        Attendance.date == body.date,
        Attendance.period == body.period,
    ).delete()

    for record in body.records:
        log = Attendance(
            student_id=record.student_id,
            class_id=body.class_id,
            date=body.date,
            period=body.period,
            status=record.status,
            reason=record.reason,
        )
        db.add(log)
    
    db.commit()
    return ApiResponse(message="考勤点名保存成功")


@router.get("/teacher/leaves")
def get_teacher_leaves(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """班主任：获取本班学生的请假审批列表"""
    cls = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(403, detail="仅班主任可审批请假单")
    
    students = db.query(Student).filter(Student.class_id == cls.id).all()
    stu_ids = [s.id for s in students]
    stu_map = {s.id: s.name for s in students}

    if not stu_ids:
        return ApiResponse(data=[])

    leaves = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.student_id.in_(stu_ids))
        .order_by(LeaveRequest.status.asc(), LeaveRequest.start_date.desc())
        .all()
    )

    data = []
    for lv in leaves:
        data.append({
            "id": lv.id,
            "student_id": lv.student_id,
            "student_name": stu_map.get(lv.student_id, "未知学生"),
            "start_date": lv.start_date.strftime("%Y-%m-%d"),
            "end_date": lv.end_date.strftime("%Y-%m-%d"),
            "reason": lv.reason,
            "status": lv.status.value,
            "approved_by": lv.approved_by,
            "feedback": lv.feedback,
        })
    return ApiResponse(data=data)


@router.put("/teacher/leaves/{request_id}")
def approve_leave_request(
    request_id: int,
    body: dict,  # status ("approved" or "rejected"), feedback (optional)
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """班主任：审批（批准或拒绝）请假申请"""
    lv = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not lv:
        raise HTTPException(404, detail="请假单不存在")
    
    # Check permission
    student = db.query(Student).filter(Student.id == lv.student_id).first()
    if not student:
        raise HTTPException(404, detail="关联学生不存在")
        
    cls = db.query(Class).filter(Class.id == student.class_id).first()
    if not cls or cls.homeroom_teacher_id != current_user.id:
        raise HTTPException(403, detail="无权操作非本班学生的请假单")
    
    req_status = body.get("status")
    if req_status not in ["approved", "rejected"]:
        raise HTTPException(400, detail="状态参数错误")
    
    lv.status = LeaveStatus(req_status)
    lv.approved_by = current_user.id
    lv.feedback = body.get("feedback", "")

    # If approved, automatically update/write 'leave' status in Attendance logs for the dates!
    if lv.status == LeaveStatus.APPROVED:
        # Loop through periods for each day in range
        curr_d = lv.start_date
        while curr_d <= lv.end_date:
            for p in range(1, 9):
                # Update or create attendance entry for this day + period
                existing_att = db.query(Attendance).filter(
                    Attendance.student_id == lv.student_id,
                    Attendance.date == curr_d,
                    Attendance.period == p
                ).first()
                
                if existing_att:
                    existing_att.status = AttendanceStatus.LEAVE
                    existing_att.reason = f"请假已批准 (单号 {lv.id})"
                else:
                    new_att = Attendance(
                        student_id=lv.student_id,
                        class_id=student.class_id,
                        date=curr_d,
                        period=p,
                        status=AttendanceStatus.LEAVE,
                        reason=f"请假已批准 (单号 {lv.id})"
                    )
                    db.add(new_att)
            curr_d += date_type.resolution  # date increment
            
    db.commit()
    return ApiResponse(message="审批完成")


# ─── 管理端接口 ───────────────────────────────────────────────

@router.get("/admin/stats")
def get_admin_attendance_stats(
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """管理员：全校考勤总览"""
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="无管理员权限")
    
    # Class-wise attendance stats
    classes = db.query(Class).all()
    data = []
    
    for cls in classes:
        logs_query = db.query(Attendance).filter(Attendance.class_id == cls.id)
        total = logs_query.count()
        present = logs_query.filter(Attendance.status == AttendanceStatus.PRESENT).count()
        tardy = logs_query.filter(Attendance.status == AttendanceStatus.TARDY).count()
        absent = logs_query.filter(Attendance.status == AttendanceStatus.ABSENT).count()
        leave = logs_query.filter(Attendance.status == AttendanceStatus.LEAVE).count()

        attendance_rate = (present / (total - leave) * 100) if (total - leave) > 0 else 100.0
        
        data.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "total": total,
            "present": present,
            "tardy": tardy,
            "absent": absent,
            "leave": leave,
            "attendance_rate": round(attendance_rate, 1),
        })

    # High risk absent students ranking
    from sqlalchemy import func
    high_absent = (
        db.query(Student.name, Class.name, func.count(Attendance.id).label("cnt"))
        .join(Attendance, Student.id == Attendance.student_id)
        .join(Class, Student.class_id == Class.id)
        .filter(Attendance.status == AttendanceStatus.ABSENT)
        .group_by(Student.id, Class.id)
        .order_by(func.count(Attendance.id).desc())
        .limit(10)
        .all()
    )

    return ApiResponse(data={
        "classes": data,
        "warnings": [
            {"student_name": sname, "class_name": cname, "absent_count": cnt}
            for sname, cname, cnt in high_absent
        ]
    })
