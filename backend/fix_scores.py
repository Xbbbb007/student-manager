"""
为二班（三年级二班，student_id 31-60）生成成绩，并重新计算所有排名
- class_rank: 班内排名（DENSE_RANK）
- school_rank: 年级排名（三年级两个班一起排，DENSE_RANK）
"""
import random
import pymysql

random.seed(42)

conn = pymysql.connect(
    host='localhost', port=3306,
    user='root', password='3274594297',
    database='student_manager', charset='utf8mb4'
)
cursor = conn.cursor()

subjects = ['chinese', 'math', 'english', 'science', 'ethics']
class2_students = list(range(31, 61))

# 获取一班各科目各考试的分数分布，作为二班的参考
cursor.execute("""
    SELECT s.exam_id, s.subject, MIN(s.score), MAX(s.score), AVG(s.score), STDDEV(s.score)
    FROM scores s
    JOIN students st ON s.student_id = st.id
    WHERE st.class_id = 1
    GROUP BY s.exam_id, s.subject
    ORDER BY s.exam_id, s.subject
""")
distributions = {}
for row in cursor.fetchall():
    exam_id, subject, min_s, max_s, avg_s, std_s = row
    distributions[(exam_id, subject)] = {
        'min': float(min_s), 'max': float(max_s),
        'avg': float(avg_s), 'std': float(std_s or 5)
    }

# 为二班生成成绩
insert_data = []
for exam_id in range(1, 7):
    for subject in subjects:
        dist = distributions[(exam_id, subject)]
        scores = []
        for _ in range(len(class2_students)):
            s = random.gauss(dist['avg'], dist['std'])
            s = max(dist['min'] - 2, min(dist['max'] + 2, s))
            s = round(s)
            s = max(0, min(100, s))
            scores.append(s)

        scores.sort(reverse=True)
        for i, student_id in enumerate(class2_students):
            insert_data.append((student_id, exam_id, subject, float(scores[i])))

# 批量插入
cursor.executemany(
    "INSERT INTO scores (student_id, exam_id, subject, score) VALUES (%s, %s, %s, %s)",
    insert_data
)
conn.commit()
print(f"已为二班插入 {len(insert_data)} 条成绩记录")

# 重新计算所有排名
cursor.execute("""
    UPDATE scores s
    JOIN students st ON s.student_id = st.id
    JOIN classes c ON st.class_id = c.id
    SET
        s.class_rank = (
            SELECT rn FROM (
                SELECT s2.id, DENSE_RANK() OVER (
                    PARTITION BY s2.exam_id, s2.subject, st2.class_id
                    ORDER BY s2.score DESC
                ) AS rn
                FROM scores s2
                JOIN students st2 ON s2.student_id = st2.id
            ) ranked WHERE ranked.id = s.id
        ),
        s.school_rank = (
            SELECT rn2 FROM (
                SELECT s3.id, DENSE_RANK() OVER (
                    PARTITION BY s3.exam_id, s3.subject, c3.grade
                    ORDER BY s3.score DESC
                ) AS rn2
                FROM scores s3
                JOIN students st3 ON s3.student_id = st3.id
                JOIN classes c3 ON st3.class_id = c3.id
            ) ranked2 WHERE ranked2.id = s.id
        )
""")
conn.commit()
print("所有排名已重新计算")

# 验证
cursor.execute("""
    SELECT st.name, c.name as class_name, s.score, s.class_rank, s.school_rank
    FROM scores s
    JOIN students st ON s.student_id = st.id
    JOIN classes c ON st.class_id = c.id
    WHERE s.exam_id = 1 AND s.subject = 'chinese'
    ORDER BY s.score DESC
""")
print("\n=== 第一次月考 语文 排名验证 ===")
print(f"{'姓名':<8} {'班级':<20} {'分数':>6} {'班排名':>6} {'级排名':>6}")
print("-" * 55)
for row in cursor.fetchall():
    name, class_name, score, cr, sr = row
    print(f"{name:<8} {class_name:<20} {score:>6.0f} {cr:>6} {sr:>6}")

cursor.close()
conn.close()
