"""课表种子数据 — 为小学部各班生成课表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from sqlalchemy import create_engine, text
from backend.database import Base, SessionLocal
from backend.models import Staff, Student, Class, Schedule

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/student_manager")
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ─── 科目配置 ─────────────────────────────────────
SUBJECT_MAP = {
    "chinese": "语文", "math": "数学", "english": "英语",
    "science": "科学", "ethics": "道德与法治", "pe": "体育",
    "music": "音乐", "art": "美术", "it": "信息科技", "self-study": "自习",
}

# ─── 小学部标准课表模板（每天6节） ───────────────────
WEEKLY_TEMPLATE = {
    1: ["chinese", "math", "english", "chinese", "pe", "music"],       # 周一
    2: ["math", "chinese", "science", "ethics", "chinese", "art"],     # 周二
    3: ["english", "chinese", "math", "art", "chinese", "pe"],         # 周三
    4: ["chinese", "math", "chinese", "pe", "science", "ethics"],      # 周四
    5: ["math", "english", "chinese", "it", "pe", "self-study"],       # 周五
}

# ─── 教师分配（按年级配置） ─────────────────────────
GRADE_TEACHERS = {
    "三年级": {
        "chinese": "张老师", "math": "李老师", "english": "王老师",
        "science": "张老师", "ethics": "李老师",
        "pe": "赵老师", "music": "周老师", "art": "吴老师",
        "it": "陈老师", "self-study": "张老师",
    },
    "四年级": {
        "chinese": "赵老师", "math": "孙老师", "english": "钱老师",
        "science": "赵老师", "ethics": "孙老师",
        "pe": "吴老师", "music": "郑老师", "art": "冯老师",
        "it": "陈老师", "self-study": "赵老师",
    },
    "五年级": {
        "chinese": "成老师", "math": "蔡老师", "english": "彭老师",
        "science": "成老师", "ethics": "蔡老师",
        "pe": "冯老师", "music": "郑老师", "art": "吴老师",
        "it": "陈老师", "self-study": "成老师",
    },
    "六年级": {
        "chinese": "许老师", "math": "何老师", "english": "高老师",
        "science": "许老师", "ethics": "何老师",
        "pe": "冯老师", "music": "郑老师", "art": "吴老师",
        "it": "陈老师", "self-study": "许老师",
    },
}

# ─── 创建课表 ─────────────────────────────────────
all_classes = db.query(Class).filter(Class.section == "小学部").all()
print(f"找到 {len(all_classes)} 个小学部班级")

total_created = 0
for cls in all_classes:
    grade = cls.grade
    teachers = GRADE_TEACHERS.get(grade, {})
    if not teachers:
        print(f"  跳过 {cls.name}（无年级教师配置）")
        continue

    db.query(Schedule).filter(Schedule.class_id == cls.id).delete()

    for day in range(1, 6):
        subjects = WEEKLY_TEMPLATE[day]
        for period, subj in enumerate(subjects, 1):
            teacher_name = teachers.get(subj, "")
            teacher = db.query(Staff).filter(Staff.name == teacher_name).first()
            teacher_id = teacher.id if teacher else None

            schedule = Schedule(
                class_id=cls.id,
                day_of_week=day,
                period=period,
                subject=subj,
                teacher_id=teacher_id,
            )
            db.add(schedule)
            total_created += 1

    db.commit()
    print(f"  OK {cls.name} - {6*5} periods")

print(f"\nDone! Total {total_created} schedule records")
db.close()
