from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from ..models.enums import AttendanceStatus, LeaveStatus


class LeaveRequestCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str


class LeaveRequestResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus
    approved_by: Optional[int] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceCreateSingle(BaseModel):
    student_id: int
    status: AttendanceStatus
    reason: Optional[str] = None


class RollCallRequest(BaseModel):
    class_id: int
    date: date
    period: int
    records: List[AttendanceCreateSingle]


class AttendanceLogResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    class_id: int
    class_name: Optional[str] = None
    date: date
    period: int
    status: AttendanceStatus
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    present: int
    tardy: int
    absent: int
    leave: int
    total: int
    attendance_rate: float
