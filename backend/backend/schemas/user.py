from pydantic import BaseModel, Field
from typing import Optional
from ..models.user import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    username: str
    name: str
    role: UserRole

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[object] = None
