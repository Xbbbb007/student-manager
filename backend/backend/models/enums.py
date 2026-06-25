import enum

class StaffRole(str, enum.Enum):
    TEACHER = "teacher"
    ADMIN = "admin"

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class Subject(str, enum.Enum):
    CHINESE = "chinese"
    MATH = "math"
    ENGLISH = "english"
    SCIENCE = "science"
    ETHICS = "ethics"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    TARDY = "tardy"
    ABSENT = "absent"
    LEAVE = "leave"

class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
