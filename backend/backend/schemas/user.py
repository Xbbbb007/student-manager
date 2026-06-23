from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StaffInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str
    user_type: str = "staff"
    subject: Optional[str] = None

    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str = "student"
    user_type: str = "student"
    class_id: Optional[int] = None

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[object] = None
