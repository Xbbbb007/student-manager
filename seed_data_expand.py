"""种子数据扩展脚本 — 补充小学部五年级、六年级及全科教师"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Staff, Student, Class, StaffRole, Gender, Subject
from backend.core.security import hash_password

engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")
Session = sessionmaker(bind=engine)
db = Session()

import random; random.seed(123)

# ─── 额外姓名池（第一批 120+120 已用完）────────────────
MORE_MALE = [
    "杜宇航","肖泽宇","戴明远","谭天宇","廖梓睿","熊浩宇","金骏杰","余子涵","罗泽宇","梁嘉豪",
    "宋致远","唐文昊","韩子轩","曹天阳","邓泽楷","冯宇晨","程俊豪","蔡浩铭","魏宇轩","胡博超",
    "林景行","何泽楷","高天阳","罗文昊","梁思远","宋伟杰","邓鹏飞","冯睿渊","韩明远","谭浩宇",
    "汤泽宇","尹子豪","汪俊杰","田泽宇","任浩铭","姜致远","范思远","方天阳","石伟杰","邹睿渊",
    "潘浩然","葛俊哲","范一鸣","彭泽宇","曾子骞","蔡景行","魏浩宇","夏泽楷","肖文昊","戴宇轩",
    "贾致远","沈思远","蒋天阳","余伟杰","廖睿渊","熊浩然","金俊哲","余一鸣","罗泽宇","梁子骞",
]
MORE_FEMALE = [
    "杜雨彤","肖语萱","戴梓涵","谭静怡","廖若曦","熊思琪","金可欣","余芷晴","罗雅文","梁欣怡",
    "宋悦然","唐梓萌","韩雨桐","曹梓萱","邓语嫣","冯思涵","程芷柔","蔡可欣","魏佳琪","胡梦洁",
    "林雅静","何梓萱","高雨欣","罗芷晴","梁梓萌","宋思涵","唐梓萌","韩语嫣","曹雨桐","邓可欣",
    "冯芷晴","韩梓萌","曹语嫣","彭思涵","曾梓萌","程雨欣","蔡芷柔","魏佳琪","胡雅静","林梦洁",
    "何思涵","高梓萌","罗雨桐","梁可欣","宋语嫣","唐雨彤","韩语萱","曹梓萱","邓静怡","冯若曦",
    "韩思琪","曹可欣","彭芷晴","曾雅文","萧欣怡","苏悦然","范梓萌","沈雨桐","韩可欣","贾语嫣",
]
random.shuffle(MORE_MALE)
random.shuffle(MORE_FEMALE)

print("=" * 60)
print("开始扩展小学部数据...")
print()

# ═══════════════════════════════════════════════
# 第一步：补充三年级、四年级的科学和道德教师
# ═══════════════════════════════════════════════

existing_teachers = {s.username: s for s in db.query(Staff).all()}
new_staff = []

grade3_subj = {
    "science": ("zhang_sci", "张科学", Subject.SCIENCE, Gender.MALE),
    "ethics":  ("zhang_eth", "张道德", Subject.ETHICS,  Gender.FEMALE),
}
grade4_subj = {
    "science": ("zhao_sci", "赵科学", Subject.SCIENCE, Gender.FEMALE),
    "ethics":  ("zhao_eth", "赵道德", Subject.ETHICS,  Gender.MALE),
}

for grade_map in [grade3_subj, grade4_subj]:
    for key, (uname, name, subj, g) in grade_map.items():
        if uname not in existing_teachers:
            t = Staff(
                username=uname,
                password_hash=hash_password("123456"),
                password_plain="123456",
                name=name,
                role=StaffRole.TEACHER,
                subject=subj,
                gender=g,
            )
            db.add(t)
            db.flush()
            new_staff.append(t)
            existing_teachers[uname] = t
            print(f"  ✅ 新增教师: {name} ({subj.value})")

# ═══════════════════════════════════════════════
# 第二步：创建五年级、六年级班级
# ═══════════════════════════════════════════════

# 先创建五年级、六年级的 5 科教师
grade5_teachers = {}
grade6_teachers = {}

grade5_subjects = [
    ("wu_chi",  "吴语文", Subject.CHINESE, Gender.FEMALE),
    ("wu_math", "吴数学", Subject.MATH,    Gender.MALE),
    ("wu_eng",  "吴英语", Subject.ENGLISH, Gender.FEMALE),
    ("wu_sci",  "吴科学", Subject.SCIENCE, Gender.MALE),
    ("wu_eth",  "吴道德", Subject.ETHICS,  Gender.FEMALE),
]
grade6_subjects = [
    ("zheng_chi",  "郑语文", Subject.CHINESE, Gender.MALE),
    ("zheng_math", "郑数学", Subject.MATH,    Gender.FEMALE),
    ("zheng_eng",  "郑英语", Subject.ENGLISH, Gender.MALE),
    ("zheng_sci",  "郑科学", Subject.SCIENCE, Gender.FEMALE),
    ("zheng_eth",  "郑道德", Subject.ETHICS,  Gender.MALE),
]

for uname, name, subj, g in grade5_subjects:
    if uname not in existing_teachers:
        t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
                  name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
        db.add(t)
        db.flush()
        new_staff.append(t)
        existing_teachers[uname] = t
    grade5_teachers[subj.value] = existing_teachers[uname]
    print(f"  ✅ 新增教师: {name} ({subj.value})")

for uname, name, subj, g in grade6_subjects:
    if uname not in existing_teachers:
        t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
                  name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
        db.add(t)
        db.flush()
        new_staff.append(t)
        existing_teachers[uname] = t
    grade6_teachers[subj.value] = existing_teachers[uname]
    print(f"  ✅ 新增教师: {name} ({subj.value})")

# 创建班级（五年级：语数英科道老师的 id，六年级同理）
# 班主任默认用语文老师
c_g5_01 = Class(name="小学部五年级一班", section="小学部", grade="五年级",
                homeroom_teacher_id=grade5_teachers["chinese"].id)
c_g5_02 = Class(name="小学部五年级二班", section="小学部", grade="五年级",
                homeroom_teacher_id=grade5_teachers["chinese"].id)
c_g6_01 = Class(name="小学部六年级一班", section="小学部", grade="六年级",
                homeroom_teacher_id=grade6_teachers["chinese"].id)
c_g6_02 = Class(name="小学部六年级二班", section="小学部", grade="六年级",
                homeroom_teacher_id=grade6_teachers["chinese"].id)

new_classes = [c_g5_01, c_g5_02, c_g6_01, c_g6_02]
for c in new_classes:
    db.add(c)
    db.flush()

print()
for c in new_classes:
    print(f"  ✅ 新增班级: {c.name} (班主任 ID={c.homeroom_teacher_id})")

# ═══════════════════════════════════════════════
# 第三步：创建学生（每班30人，男女各15）
# ═══════════════════════════════════════════════

# 学号映射
new_class_code = {
    c_g5_01.id: ("01", "05", "01"),
    c_g5_02.id: ("01", "05", "02"),
    c_g6_01.id: ("01", "06", "01"),
    c_g6_02.id: ("01", "06", "02"),
}

total_new_students = 0

for c in new_classes:
    sc, gc, cc = new_class_code[c.id]
    for seq in range(1, 16):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = MORE_MALE.pop()
        db.add(Student(username=username, password_hash=hash_password("123456"),
                        password_plain="123456", name=name, gender=Gender.MALE, class_id=c.id))
        total_new_students += 1
    for seq in range(16, 31):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = MORE_FEMALE.pop()
        db.add(Student(username=username, password_hash=hash_password("123456"),
                        password_plain="123456", name=name, gender=Gender.FEMALE, class_id=c.id))
        total_new_students += 1

db.commit()
db.close()

print()
print("=" * 60)
print("✅ 小学部数据扩展完成！")
print(f"  🔸 新增教师: {len(new_staff)}人")
print(f"  🔸 新增班级: {len(new_classes)}个")
print(f"  🔸 新增学生: {total_new_students}人")
print()
print("班级列表:")
for c in new_classes:
    sc, gc, cc = new_class_code[c.id]
    print(f"  {c.name:20s} → 学号前缀 {sc}{gc}{cc}XX")
print()
print("新增教师明细:")
for t in new_staff:
    print(f"  {t.name:10s} ({t.username:15s}) → {t.subject.value}")
print()
print("密码统一: 123456")
print("=" * 60)
