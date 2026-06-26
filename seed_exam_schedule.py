import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models import Class, Subject
from backend.models.exam_schedule import ExamSchedule

engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")
# Create the tables
print("Creating tables if they don't exist...")
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
db = Session()

# Check if we already have exam schedules seeded
if db.query(ExamSchedule).count() > 0:
    print("Exam schedules already seeded.")
    sys.exit(0)

# Get Grade 3 Class 1 and Class 2
c1 = db.query(Class).filter(Class.name.like("%三年级%一班%")).first()
c2 = db.query(Class).filter(Class.name.like("%三年级%二班%")).first()

if not c1 or not c2:
    print("Required classes not found.")
    sys.exit(1)

print(f"Seeding exam schedules for class: {c1.name} and {c2.name}")

# Seeding schedules for Class 1 (No conflict)
scheds = [
    # Chinese
    ExamSchedule(
        name="2025年第一学期语文期末大考",
        class_id=c1.id,
        subject=Subject.CHINESE,
        exam_date=date(2026, 6, 28),
        start_time="09:00",
        end_time="11:30",
        location="教学楼二楼一班教室",
        status="未开始",
    ),
    # Math
    ExamSchedule(
        name="2025年第一学期数学期末大考",
        class_id=c1.id,
        subject=Subject.MATH,
        exam_date=date(2026, 6, 29),
        start_time="09:00",
        end_time="11:00",
        location="教学楼二楼一班教室",
        status="未开始",
    ),
    # English
    ExamSchedule(
        name="2025年第一学期英语期末大考",
        class_id=c1.id,
        subject=Subject.ENGLISH,
        exam_date=date(2026, 6, 30),
        start_time="14:00",
        end_time="15:30",
        location="实验楼二楼机房",
        status="未开始",
    ),
    # Completed exam (Class 1)
    ExamSchedule(
        name="三年级第一单元语文摸底考",
        class_id=c1.id,
        subject=Subject.CHINESE,
        exam_date=date(2026, 6, 10),
        start_time="09:00",
        end_time="10:00",
        location="教学楼二楼一班教室",
        status="已结束",
    ),
]

# Seeding schedules for Class 2 (Includes a conflict for testing admin feature)
scheds += [
    # Conflicting Math exam on 2026-06-28
    ExamSchedule(
        name="2025年第一学期数学期末大考",
        class_id=c2.id,
        subject=Subject.MATH,
        exam_date=date(2026, 6, 28),
        start_time="09:00",
        end_time="11:00",
        location="教学楼二楼二班教室",
        status="未开始",
    ),
    # Conflicting Science exam on 2026-06-28 (Same day)
    ExamSchedule(
        name="2025年第一学期科学期末大考",
        class_id=c2.id,
        subject=Subject.SCIENCE,
        exam_date=date(2026, 6, 28),
        start_time="14:00",
        end_time="15:30",
        location="实验楼一楼物理实验室",
        status="未开始",
    ),
]

db.add_all(scheds)
db.commit()
print("Successfully seeded exam schedules data!")
