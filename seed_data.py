"""一体化种子数据生成脚本 - 极速种植并计算所有表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import random
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pymysql

from backend.database import Base
from backend.models import Staff, Student, Class, StaffRole, Gender, Subject, TeacherClass, Schedule, Exam, Score
from backend.core.security import hash_password

# 1. 预先计算哈希，极大提升性能
print("正在计算默认密码哈希...")
hash_123456 = hash_password("123456")
hash_admin123 = hash_password("admin123")
print("密码哈希计算完成！")

# 2. 连接数据库并清除旧数据
engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")
with engine.connect() as conn:
    print("清空旧数据中...")
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.execute(text("TRUNCATE TABLE scores"))
    conn.execute(text("TRUNCATE TABLE exams"))
    conn.execute(text("TRUNCATE TABLE schedules"))
    conn.execute(text("TRUNCATE TABLE teacher_classes"))
    conn.execute(text("TRUNCATE TABLE students"))
    conn.execute(text("TRUNCATE TABLE classes"))
    conn.execute(text("TRUNCATE TABLE staff"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()
print("表已清空。")

Session = sessionmaker(bind=engine)
db = Session()

random.seed(42)

# 3. 创建管理员
admin = Staff(
    username="admin", 
    password_hash=hash_admin123,
    password_plain="admin123", 
    name="系统管理员", 
    role=StaffRole.ADMIN
)
db.add(admin)
db.flush()

# 4. 创建教师账号
teachers_config = [
    # 三年级（小学）
    ("zhang_laoshi", "张老师", Subject.CHINESE, Gender.MALE),
    ("li_laoshi",   "李老师", Subject.MATH,   Gender.FEMALE),
    ("wang_laoshi", "王老师", Subject.ENGLISH, Gender.FEMALE),
    ("zhang_sci",   "张科学", Subject.SCIENCE, Gender.MALE),
    ("zhang_eth",   "张道德", Subject.ETHICS,  Gender.FEMALE),

    # 四年级（小学）
    ("zhao_laoshi", "赵老师", Subject.CHINESE, Gender.FEMALE),
    ("sun_laoshi",  "孙老师", Subject.MATH,   Gender.MALE),
    ("qian_laoshi", "钱老师", Subject.ENGLISH, Gender.MALE),
    ("zhao_sci",   "赵科学", Subject.SCIENCE, Gender.FEMALE),
    ("zhao_eth",   "赵道德", Subject.ETHICS,  Gender.MALE),

    # 五年级（小学）
    ("wu_chi",      "吴语文", Subject.CHINESE, Gender.FEMALE),
    ("wu_math",     "吴数学", Subject.MATH,    Gender.MALE),
    ("wu_eng",      "吴英语", Subject.ENGLISH, Gender.FEMALE),
    ("wu_sci",      "吴科学", Subject.SCIENCE, Gender.MALE),
    ("wu_eth",      "吴道德", Subject.ETHICS,  Gender.FEMALE),

    # 六年级（小学）
    ("zheng_chi",   "郑语文", Subject.CHINESE, Gender.MALE),
    ("zheng_math",  "郑数学", Subject.MATH,    Gender.FEMALE),
    ("zheng_eng",   "郑英语", Subject.ENGLISH, Gender.MALE),
    ("zheng_sci",   "郑科学", Subject.SCIENCE, Gender.FEMALE),
    ("zheng_eth",   "郑道德", Subject.ETHICS,  Gender.MALE),

    # 初中一年级
    ("chen_laoshi", "陈老师", Subject.CHINESE, Gender.FEMALE),
    ("yang_laoshi", "杨老师", Subject.MATH,   Gender.MALE),
    ("liu_laoshi",  "刘老师", Subject.ENGLISH, Gender.FEMALE),

    # 初中二年级
    ("huang_laoshi","黄老师", Subject.CHINESE, Gender.MALE),
    ("zhou_laoshi", "周老师", Subject.MATH,   Gender.FEMALE),
    ("wu_laoshi",   "吴老师", Subject.ENGLISH, Gender.MALE),
]

teachers = {}
for uname, name, subj, g in teachers_config:
    t = Staff(
        username=uname,
        password_hash=hash_123456,
        password_plain="123456",
        name=name,
        role=StaffRole.TEACHER,
        subject=subj,
        gender=g
    )
    db.add(t)
    db.flush()
    teachers[uname] = t

print(f"教职工创建完毕：{len(teachers_config) + 1}人")

# 5. 创建班级
classes_config = [
    ("小学部三年级一班", "小学部", "三年级", "zhang_laoshi"),
    ("小学部三年级二班", "小学部", "三年级", "li_laoshi"),
    ("小学部四年级一班", "小学部", "四年级", "zhao_laoshi"),
    ("小学部四年级二班", "小学部", "四年级", "sun_laoshi"),
    ("小学部五年级一班", "小学部", "五年级", "wu_chi"),
    ("小学部五年级二班", "小学部", "五年级", "wu_math"),
    ("小学部六年级一班", "小学部", "六年级", "zheng_chi"),
    ("小学部六年级二班", "小学部", "六年级", "zheng_math"),
    ("初中部一年级一班", "初中部", "一年级", "chen_laoshi"),
    ("初中部一年级二班", "初中部", "一年级", "yang_laoshi"),
    ("初中部二年级一班", "初中部", "二年级", "huang_laoshi"),
    ("初中部二年级二班", "初中部", "二年级", "zhou_laoshi"),
]

classes = {}
for cname, section, grade, homeroom_uname in classes_config:
    teacher = teachers.get(homeroom_uname)
    c = Class(
        name=cname,
        section=section,
        grade=grade,
        homeroom_teacher_id=teacher.id if teacher else None
    )
    db.add(c)
    db.flush()
    classes[cname] = c

print(f"班级创建完毕：{len(classes_config)}个")

# 6. 教师任教关联表 (teacher_classes)
assignments = []
# 小学部三年级
for uname, subj in [("zhang_laoshi", "chinese"), ("li_laoshi", "math"), ("wang_laoshi", "english"), ("zhang_sci", "science"), ("zhang_eth", "ethics")]:
    assignments.extend([(uname, "小学部三年级一班", subj), (uname, "小学部三年级二班", subj)])
# 小学部四年级
for uname, subj in [("zhao_laoshi", "chinese"), ("sun_laoshi", "math"), ("qian_laoshi", "english"), ("zhao_sci", "science"), ("zhao_eth", "ethics")]:
    assignments.extend([(uname, "小学部四年级一班", subj), (uname, "小学部四年级二班", subj)])
# 五年级
for uname, subj in [("wu_chi", "chinese"), ("wu_math", "math"), ("wu_eng", "english"), ("wu_sci", "science"), ("wu_eth", "ethics")]:
    assignments.extend([(uname, "小学部五年级一班", subj), (uname, "小学部五年级二班", subj)])
# 六年级
for uname, subj in [("zheng_chi", "chinese"), ("zheng_math", "math"), ("zheng_eng", "english"), ("zheng_sci", "science"), ("zheng_eth", "ethics")]:
    assignments.extend([(uname, "小学部六年级一班", subj), (uname, "小学部六年级二班", subj)])
# 初中一年级
for uname, subj in [("chen_laoshi", "chinese"), ("yang_laoshi", "math"), ("liu_laoshi", "english")]:
    assignments.extend([(uname, "初中部一年级一班", subj), (uname, "初中部一年级二班", subj)])
# 初中二年级
for uname, subj in [("huang_laoshi", "chinese"), ("zhou_laoshi", "math"), ("wu_laoshi", "english")]:
    assignments.extend([(uname, "初中部二年级一班", subj), (uname, "初中部二年级二班", subj)])

for uname, cname, subj in assignments:
    t = teachers[uname]
    c = classes[cname]
    db.add(TeacherClass(teacher_id=t.id, class_id=c.id, subject=subj))
db.flush()
print(f"教师任教映射创建完毕：{len(assignments)}条")

# 7. 姓名池与学生创建
MALE_NAMES = ["刘子轩","陈浩宇","杨明远","赵天宇","黄梓涵","周子涵","吴俊杰","徐子豪","孙泽宇","马浩然",
    "朱宇航","胡文博","林伟杰","何思远","高天阳","罗宇轩","梁嘉豪","宋致远","唐文昊","许泽楷",
    "邓睿轩","冯俊哲","韩一鸣","曹博文","彭子骞","曾鹏飞","萧景行","程子墨","蔡子轩","魏浩然",
    "郑天翔","谢宇轩","谭浩铭","蒋睿泽","沈子骞","韩景行","贾博超","夏宇晨","苏睿渊","范一鸣",
    "方泽楷","石致远","姚天阳","廖文昊","熊子轩","金明远","余浩宇","潘梓涵","龚子豪","陆泽宇",
    "孔浩然","崔俊杰","白子涵","武文博","史思远","贺天宇","顾宇航","乔伟杰","汪子豪","邱泽宇",
    "叶昊天","龙泽宇","侯俊豪","邵宇晨","杜宇航","肖泽宇","戴明远","谭天宇","廖梓睿","熊浩宇",
    "金骏杰","余子涵","罗泽宇","梁嘉豪","宋致远","唐文昊","韩子轩","曹天阳","邓泽楷","冯宇晨",
    "程俊豪","蔡浩铭","魏宇轩","胡博超","林景行","何泽楷","高天阳","罗文昊","梁思远","宋伟杰",
    "邓鹏飞","冯睿渊","韩明远","谭浩宇","汤泽宇","尹子豪","汪俊杰","田泽宇","任浩铭","姜致远",
    "范思远","方天阳","石伟杰","邹睿渊","潘浩然","葛俊哲","范一鸣","彭泽宇","曾子骞","蔡景行",
    "魏浩宇","夏泽楷","肖文昊","戴宇轩","贾致远","沈思远","蒋天阳","余伟杰","廖睿渊","熊浩然",
    "金俊哲","余一鸣","罗泽宇","梁子骞","马建国","王建军","张伟","李强","刘洋","陈杰",
    "宋伟","唐超","韩峰","彭伟","曾凡","程建","蔡敏","魏军","廖波","余兵"]

FEMALE_NAMES = ["陈雨桐","张语萱","王子涵","李若曦","赵梦瑶","刘诗琪","杨雅婷","黄思琪","周婉晴","吴思颖",
    "徐欣怡","孙悦然","马可欣","朱芷晴","胡梓涵","林静怡","何思琪","高梓萱","罗雨欣","梁芷柔",
    "宋佳琪","唐雅静","梦洁","邓思涵","冯梓萌","韩雨桐","曹可欣","彭语嫣","曾芷晴","萧雅文",
    "苏雨桐","范语萱","沈梓涵","韩若曦","贾梦瑶","夏诗琪","廖雅婷","熊思琪","金婉晴","余思颖",
    "潘欣怡","龚悦然","陆可欣","孔芷晴","白梓涵","崔静怡","武思琪","史梓萱","贺雨欣","顾芷柔",
    "乔佳琪","汪雅静","邱梦洁","苏思涵","杜雨彤","语萱","戴梓涵","谭静怡","廖若曦","熊思琪",
    "金可欣","余芷晴","罗雅文","梁欣怡","宋悦然","唐梓萌","韩雨桐","曹梓萱","邓语嫣","冯思涵",
    "程芷柔","蔡可欣","魏佳琪","胡梦洁","林雅静","何梓萱","高雨欣","罗芷晴","梁梓萌","宋思涵",
    "唐梓萌","韩语嫣","曹雨桐","邓可欣","冯芷晴","韩梓萌","曹语嫣","彭思涵","曾梓萌","程雨欣",
    "蔡芷柔","魏佳琪","胡雅静","林梦洁","何思涵","高梓萌","罗雨桐","梁可欣","宋语嫣","唐雨彤",
    "韩语萱","曹梓萱","邓静怡","冯若曦","韩思琪","曹可欣","彭芷晴","曾雅文","萧欣怡","苏悦然",
    "范梓萌","沈雨桐","韩可欣","贾语嫣","夏芷晴","廖雅文","李秀英","张秀兰","王秀珍","王红",
    "李丽","李娜","张艳","张敏","张洋","刘敏","王燕","李敏","陈娟","张涛"]

random.shuffle(MALE_NAMES)
random.shuffle(FEMALE_NAMES)

name_pool_male = list(set(MALE_NAMES))
name_pool_female = list(set(FEMALE_NAMES))

# 兜底生成真实中国姓名
SURNAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周", "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗", "郑", "梁", "谢", "宋", "唐", "许", "韩", "冯", "邓", "曹", "彭", "曾", "肖", "田", "董", "袁", "潘", "于", "蒋", "蔡", "余", "杜", "叶", "程", "苏", "魏", "吕", "丁", "沈", "任", "姚", "卢", "姜", "崔", "钟", "谭", "陆", "汪", "范", "金", "石", "廖", "贾", "夏", "韦", "付", "方", "白", "邹", "孟", "熊", "秦", "邱", "江", "尹", "薛", "郝", "段", "雷", "钱", "覃", "武", "乔", "常", "贺", "赖", "龚", "文"]
MALE_CHARS = ["伟", "强", "军", "磊", "洋", "勇", "杰", "涛", "超", "明", "刚", "平", "辉", "鹏", "华", "飞", "科", "宇", "轩", "俊", "豪", "梓", "睿", "建", "国", "文", "博", "浩", "然"]
FEMALE_CHARS = ["婷", "雪", "莉", "静", "丽", "敏", "燕", "艳", "娟", "雅", "倩", "婕", "馨", "欣", "涵", "梓", "萱", "琪", "诗", "若", "曦", "可", "梦", "怡", "雨", "彤", "欣", "悦", "佳", "茹"]

while len(name_pool_male) < 220:
    new_name = random.choice(SURNAMES) + random.choice(MALE_CHARS) + (random.choice(MALE_CHARS) if random.random() > 0.3 else "")
    if new_name not in name_pool_male:
        name_pool_male.append(new_name)

while len(name_pool_female) < 220:
    new_name = random.choice(SURNAMES) + random.choice(FEMALE_CHARS) + (random.choice(FEMALE_CHARS) if random.random() > 0.3 else "")
    if new_name not in name_pool_female:
        name_pool_female.append(new_name)

CLASS_CODE = {
    "小学部三年级一班": ("01", "03", "01"),
    "小学部三年级二班": ("01", "03", "02"),
    "小学部四年级一班": ("01", "04", "01"),
    "小学部四年级二班": ("01", "04", "02"),
    "小学部五年级一班": ("01", "05", "01"),
    "小学部五年级二班": ("01", "05", "02"),
    "小学部六年级一班": ("01", "06", "01"),
    "小学部六年级二班": ("01", "06", "02"),
    "初中部一年级一班": ("02", "01", "01"),
    "初中部一年级二班": ("02", "01", "02"),
    "初中部二年级一班": ("02", "02", "01"),
    "初中部二年级二班": ("02", "02", "02"),
}

students_in_classes = {} # {c_id: [student_objects]}
student_base_scores = {} # {student_id: {subject: base_score}}

total_students = 0
for cname, c in classes.items():
    sc, gc, cc = CLASS_CODE[cname]
    students_in_classes[c.id] = []
    # 每班 15 男 + 15 女 = 30 人
    for seq in range(1, 16):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = name_pool_male.pop()
        stu = Student(
            username=username, 
            password_hash=hash_123456,
            password_plain="123456", 
            name=name, 
            gender=Gender.MALE, 
            class_id=c.id
        )
        db.add(stu)
        db.flush()
        students_in_classes[c.id].append(stu)
        total_students += 1
    for seq in range(16, 31):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = name_pool_female.pop()
        stu = Student(
            username=username, 
            password_hash=hash_123456,
            password_plain="123456", 
            name=name, 
            gender=Gender.FEMALE, 
            class_id=c.id
        )
        db.add(stu)
        db.flush()
        students_in_classes[c.id].append(stu)
        total_students += 1

print(f"学生创建完毕：{total_students}人")

# 8. 课表数据种植 (schedules)
# 只为小学部 8 个班生成课表
WEEKLY_TEMPLATE_1 = {
    1: ["chinese", "math", "english", "chinese", "pe", "music"],
    2: ["math", "chinese", "science", "ethics", "chinese", "art"],
    3: ["english", "chinese", "math", "art", "chinese", "pe"],
    4: ["chinese", "math", "chinese", "pe", "science", "ethics"],
    5: ["math", "english", "chinese", "it", "pe", "self-study"],
}
WEEKLY_TEMPLATE_2 = {
    1: ["math", "english", "chinese", "pe", "music", "chinese"],
    2: ["chinese", "science", "math", "chinese", "art", "ethics"],
    3: ["chinese", "math", "english", "chinese", "pe", "art"],
    4: ["math", "chinese", "pe", "science", "ethics", "chinese"],
    5: ["english", "chinese", "it", "pe", "self-study", "math"],
}

# 教师名称到教师对象的快捷映射
teacher_obj_by_name = {t.name: t for t in db.query(Staff).all()}

# 校正后真实的教师名字映射
GRADE_TEACHERS = {
    "三年级": {
        "chinese": "张老师", "math": "李老师", "english": "王老师",
        "science": "张科学", "ethics": "张道德",
        "pe": "赵老师", "music": "周老师", "art": "吴老师",
        "it": "陈老师", "self-study": "张老师",
    },
    "四年级": {
        "chinese": "赵老师", "math": "孙老师", "english": "钱老师",
        "science": "赵科学", "ethics": "赵道德",
        "pe": "吴老师", "music": "郑老师", "art": "冯老师",
        "it": "陈老师", "self-study": "赵老师",
    },
    "五年级": {
        "chinese": "吴语文", "math": "吴数学", "english": "吴英语",
        "science": "吴科学", "ethics": "吴道德",
        "pe": "冯老师", "music": "郑老师", "art": "吴老师",
        "it": "陈老师", "self-study": "吴语文",
    },
    "六年级": {
        "chinese": "郑语文", "math": "郑数学", "english": "郑英语",
        "science": "郑科学", "ethics": "郑道德",
        "pe": "冯老师", "music": "郑老师", "art": "吴老师",
        "it": "陈老师", "self-study": "郑语文",
    },
}

# 生成临时 schedules 列表
temp_schedules = []
for cname, c in classes.items():
    if c.section != "小学部":
        continue
    grade = c.grade
    g_teachers = GRADE_TEACHERS.get(grade, {})
    template = WEEKLY_TEMPLATE_2 if "二班" in cname else WEEKLY_TEMPLATE_1
    for day in range(1, 6):
        subjects = template[day]
        for period, subj in enumerate(subjects, 1):
            tname = g_teachers.get(subj, "")
            t_obj = teacher_obj_by_name.get(tname)
            temp_schedules.append({
                "class_id": c.id,
                "day": day,
                "period": period,
                "subject": subj,
                "teacher_id": t_obj.id if t_obj else None,
                "teacher_name": tname,
            })

# 运行启发式冲突消除算法，确保同一时间任何老师不会分身上课
max_attempts = 1000
for attempt in range(max_attempts):
    conflict_found = False
    teacher_busy = {} # {(day, period): [list of (idx, teacher_id)]}
    for idx, s in enumerate(temp_schedules):
        t_id = s["teacher_id"]
        if not t_id:
            continue
        key = (s["day"], s["period"])
        if key not in teacher_busy:
            teacher_busy[key] = []
        teacher_busy[key].append((idx, t_id))
        
    for key, items in teacher_busy.items():
        t_ids = [t for _, t in items]
        duplicate_teachers = set([t for t in t_ids if t_ids.count(t) > 1])
        if duplicate_teachers:
            conflict_found = True
            for t in duplicate_teachers:
                conflict_indices = [idx for idx, tid in items if tid == t]
                target_idx = conflict_indices[0]
                target_sched = temp_schedules[target_idx]
                
                # 同班级内全周跨天对调候选
                candidates = [idx for idx, other in enumerate(temp_schedules) 
                             if other["class_id"] == target_sched["class_id"] 
                             and (other["day"] != target_sched["day"] or other["period"] != target_sched["period"])]
                if candidates:
                    other_idx = random.choice(candidates)
                    other_sched = temp_schedules[other_idx]
                    
                    # 进行对调
                    target_sched["subject"], other_sched["subject"] = other_sched["subject"], target_sched["subject"]
                    target_sched["teacher_id"], other_sched["teacher_id"] = other_sched["teacher_id"], target_sched["teacher_id"]
                    target_sched["teacher_name"], other_sched["teacher_name"] = other_sched["teacher_name"], target_sched["teacher_name"]
            break
            
    if not conflict_found:
        print(f"排课教师冲突在第 {attempt} 次迭代中完全消除！")
        break
else:
    print("警告：排课迭代达到上限，可能仍有教师冲突！")

# 验证并保存到数据库
schedule_count = 0
for s in temp_schedules:
    sched = Schedule(
        class_id=s["class_id"],
        day_of_week=s["day"],
        period=s["period"],
        subject=s["subject"],
        teacher_id=s["teacher_id"]
    )
    db.add(sched)
    schedule_count += 1

db.flush()
print(f"小学部周课表创建完毕：{schedule_count}节次")

# 9. 考试安排与成绩数据种植 (exams, scores)
exam_names = ["第一次月考", "第二次月考", "期中考试", "第三次月考", "第四次月考", "期末考试"]
exam_dates = [
    date(2024, 10, 15),
    date(2024, 11, 10),
    date(2024, 11, 28),
    date(2024, 12, 15),
    date(2025, 1, 5),
    date(2025, 1, 20),
]

# 首先，为所有学生初始化他们的科目基础分数（小学5科，初中3科）
for cname, c in classes.items():
    subjects = ["chinese", "math", "english", "science", "ethics"] if c.section == "小学部" else ["chinese", "math", "english"]
    for stu in students_in_classes[c.id]:
        student_base_scores[stu.id] = {
            subj: random.randint(62, 92) for subj in subjects
        }

# 按年级对班级进行分组，以计算校内（年级）排名
grade_classes = {} # {(section, grade): [class_objects]}
for cname, c in classes.items():
    key = (c.section, c.grade)
    if key not in grade_classes:
        grade_classes[key] = []
    grade_classes[key].append(c)

print("生成考试及成绩数据中...")
for exam_idx, exam_name in enumerate(exam_names):
    exam_date = exam_dates[exam_idx]
    
    # 针对每一个年级的各个班，生成考试记录和成绩
    for (section, grade), class_list in grade_classes.items():
        # 首先为每个班在此次考试创建 Exam
        exams_in_grade = {} # {class_id: Exam}
        for c in class_list:
            ex = Exam(
                name=exam_name,
                class_id=c.id,
                exam_date=exam_date
            )
            db.add(ex)
            db.flush()
            exams_in_grade[c.id] = ex
            
        # 对于每个年级（比如三年级的所有 2 个班），合并该年级所有学科的分数来计算 school_rank
        subjects = ["chinese", "math", "english", "science", "ethics"] if section == "小学部" else ["chinese", "math", "english"]
        
        for subj in subjects:
            # 记录所有该年级学生在此科目的成绩
            # (student_id, score_value, class_id, exam_id)
            all_grade_scores = []
            for c in class_list:
                ex = exams_in_grade[c.id]
                for stu in students_in_classes[c.id]:
                    base = student_base_scores[stu.id][subj]
                    # 模拟考试波动力度：-6 到 +8 之间
                    val = base + random.randint(-6, 8)
                    # 强力波动（如有），允许少部分人超常或失常，约束在 45 - 100 之间
                    val = max(45.0, min(100.0, float(val)))
                    
                    # 如果是语文和英语，可能带小数部分（例如 .5 分）
                    if subj in ["chinese", "english"] and random.random() > 0.5:
                        val += 0.5
                        
                    all_grade_scores.append({
                        "student_id": stu.id,
                        "class_id": c.id,
                        "exam_id": ex.id,
                        "score": val
                    })
            
            # 计算年级排名 (school_rank)
            # 使用 RANK 逻辑 (与 backend/routers/scores.py 中 DENSE_RANK 实际实现一致，即 1, 1, 3 排名跳过)
            all_grade_scores.sort(key=lambda x: x["score"], reverse=True)
            prev_score = None
            current_school_rank = 0
            for idx, item in enumerate(all_grade_scores, 1):
                if prev_score is None or item["score"] < prev_score:
                    current_school_rank = idx
                prev_score = item["score"]
                item["school_rank"] = current_school_rank
                
            # 计算各班的班内排名 (class_rank)
            for c in class_list:
                class_scores = [x for x in all_grade_scores if x["class_id"] == c.id]
                class_scores.sort(key=lambda x: x["score"], reverse=True)
                prev_class_score = None
                current_class_rank = 0
                for idx, item in enumerate(class_scores, 1):
                    if prev_class_score is None or item["score"] < prev_class_score:
                        current_class_rank = idx
                    prev_class_score = item["score"]
                    item["class_rank"] = current_class_rank

            # 将本年级所有人的成绩插入 scores 表
            for item in all_grade_scores:
                sc_record = Score(
                    student_id=item["student_id"],
                    exam_id=item["exam_id"],
                    subject=Subject(subj),
                    score=item["score"],
                    class_rank=item["class_rank"],
                    school_rank=item["school_rank"]
                )
                db.add(sc_record)
        
        db.flush()

db.commit()
db.close()

# 验证当前行数
conn = pymysql.connect(host='localhost', user='root', password='3274594297', database='student_manager')
cur = conn.cursor()
print("\n" + "="*50)
print("种子数据写入成功！目前数据库内各表统计如下：")
for t in ['staff', 'students', 'classes', 'exams', 'scores', 'teacher_classes', 'schedules']:
    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
    print(f"  - 表 {t:15s} 数据行数: {cur.fetchone()[0]}")
print("="*50)
conn.close()
