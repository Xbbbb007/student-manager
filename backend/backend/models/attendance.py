from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SAEnum, Text
from ..database import Base
from .enums import AttendanceStatus, LeaveStatus


class Attendance(Base):
    """考勤明细表"""

    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)  # 课节数 1-8
    status = Column(
        SAEnum(AttendanceStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    reason = Column(String(200), nullable=True)  # 请假说明或备注


class LeaveRequest(Base):
    """请假申请表"""

    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(
        SAEnum(LeaveStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=LeaveStatus.PENDING,
    )
    approved_by = Column(Integer, ForeignKey("staff.id"), nullable=True)
    feedback = Column(Text, nullable=True)
