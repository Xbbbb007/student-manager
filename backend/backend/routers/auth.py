from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas.user import LoginRequest, TokenResponse, StaffInfo, StudentInfo, ApiResponse
from ..services.auth import authenticate_staff, authenticate_student, get_staff_by_id, get_student_by_id
from ..core.security import create_access_token, decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Try staff table first (teachers and admins)
    staff = authenticate_staff(db, request.username, request.password)
    if staff:
        token = create_access_token({
            "sub": str(staff.id),
            "role": staff.role.value,
            "user_type": "staff"
        })
        return ApiResponse(data=TokenResponse(access_token=token))

    # Then try student table
    student = authenticate_student(db, request.username, request.password)
    if student:
        token = create_access_token({
            "sub": str(student.id),
            "role": "student",
            "user_type": "student"
        })
        return ApiResponse(data=TokenResponse(access_token=token))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误"
    )


@router.get("/me", response_model=ApiResponse)
def get_me(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Token 格式错误")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 无效")

    user_type = payload.get("user_type", "staff")
    user_id = int(payload.get("sub", 0))

    if user_type == "student":
        user = get_student_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return ApiResponse(data=StudentInfo.model_validate(user))
    else:
        user = get_staff_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return ApiResponse(data=StaffInfo.model_validate(user))
