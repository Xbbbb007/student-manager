import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models import Student, Class, Staff, Subject
from backend.models.homework import Homework, HomeworkSubmission

engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")
# Create the homework tables
print("Creating tables if they don't exist...")
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
db = Session()

# Check if we already have homework seeded
if db.query(Homework).count() > 0:
    print("Homework already seeded.")
    sys.exit(0)

# Get some teachers
zhang = db.query(Staff).filter(Staff.username == "zhang_laoshi").first()  # chinese teacher
li = db.query(Staff).filter(Staff.username == "li_laoshi").first()        # math teacher

# Get Grade 3 Class 1
class1 = db.query(Class).filter(Class.name.like("%三年级%一班%")).first()
if not class1:
    class1 = db.query(Class).first()

if not class1 or not zhang or not li:
    print("Required seed teachers/classes not found.")
    sys.exit(1)

print(f"Seeding homework for class: {class1.name}")

# Create homework assignments
hw1 = Homework(
    title="《背影》阅读理解与段落分析",
    description="请阅读朱自清的《背影》，写出你最感动的一处细节，并简要分析其写作手法。字数要求在150字以上。",
    subject=Subject.CHINESE,
    class_id=class1.id,
    teacher_id=zhang.id,
    due_date=datetime.now() + timedelta(days=2),
)

hw2 = Homework(
    title="一元一次方程课后巩固与练习题",
    description="完成课本第45页第1、2、5题。要求写出详细的解题步骤，拍照或打字提交。",
    subject=Subject.MATH,
    class_id=class1.id,
    teacher_id=li.id,
    due_date=datetime.now() + timedelta(days=1),
)

hw3 = Homework(
    title="古诗词三首背默作业",
    description="背诵并默写《登鹳雀楼》《望庐山瀑布》《赠汪伦》。请在此处输入默写内容。",
    subject=Subject.CHINESE,
    class_id=class1.id,
    teacher_id=zhang.id,
    due_date=datetime.now() - timedelta(days=1),  # Past due date (unsubmitted or graded)
)

db.add_all([hw1, hw2, hw3])
db.commit()
db.refresh(hw1)
db.refresh(hw2)
db.refresh(hw3)

# Get some students from Grade 3 Class 1
students = db.query(Student).filter(Student.class_id == class1.id).all()

# Create submissions for hw3 (already past due)
print(f"Creating submissions for {len(students)} students...")
for idx, s in enumerate(students):
    # Some students submitted, some graded, some unsubmitted
    if idx % 5 == 0:
        # Unsubmitted
        continue
    elif idx % 5 in [1, 2]:
        # Submitted, ungraded
        sub = HomeworkSubmission(
            homework_id=hw3.id,
            student_id=s.id,
            content=f"【默写内容 - {s.name}】\n白日依山尽，黄河入海流...\n飞流直下三千尺，疑是银河落九天...",
            status="submitted",
        )
        db.add(sub)
    else:
        # Graded
        score = 90.0 + (idx % 10)
        sub = HomeworkSubmission(
            homework_id=hw3.id,
            student_id=s.id,
            content=f"【默写内容 - {s.name}】\n白日依山尽，黄河入海流，欲穷千里目，更上一层楼。白发三千丈...",
            grade=score,
            feedback=f"默写很工整，继续保持！" if score >= 95 else "有个别错别字，注意复习。",
            status="graded",
        )
        db.add(sub)

# Let's also submit math homework (hw2) for student 01030106
s_01030106 = db.query(Student).filter(Student.username == "01030106").first()
if s_01030106:
    sub_math = HomeworkSubmission(
        homework_id=hw2.id,
        student_id=s_01030106.id,
        content="第1题: x + 5 = 12 => x = 7\n第2题: 2x - 3 = 7 => 2x = 10 => x = 5\n第5题: 3x = 15 => x = 5",
        status="submitted",
    )
    db.add(sub_math)

db.commit()
print("Successfully seeded homework data!")
