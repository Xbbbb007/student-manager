"""课表 schema"""
from pydantic import BaseModel
from typing import Optional, List


class ScheduleCreate(BaseModel):
    class_id: int
    day_of_week: int  # 1-5
    period: int  # 1-8
    subject: str
    teacher_id: Optional[int] = None


class ScheduleBatchCreate(BaseModel):
    """批量创建/更新课表"""
    class_id: int
    items: List[ScheduleCreate]


class ScheduleItem(BaseModel):
    id: int
    class_id: int
    day_of_week: int
    period: int
    subject: str
    subject_name: str  # 中文科目名
    teacher_id: Optional[int] = None
    teacher_name: str = ""
