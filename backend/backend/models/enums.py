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
