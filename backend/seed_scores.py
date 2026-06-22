import random
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='123456', db='student_manager')
cursor = conn.cursor()

cursor.execute("SELECT id FROM students WHERE class_id = 1 ORDER BY id")
student_ids = [r[0] for r in cursor.fetchall()]

exam_ids = list(range(1, 7))
subjects = ['chinese', 'math', 'english', 'science', 'ethics']

for exam_id in exam_ids:
    exam_scores = {}
    for sid in student_ids:
        scores = {}
        for subj in subjects:
            base = random.randint(65, 95)
            scores[subj] = base
        total = sum(scores.values())
        exam_scores[sid] = (scores, total)

    sorted_by_total = sorted(exam_scores.items(), key=lambda x: x[1][1], reverse=True)
    school_rank_map = {sid: rank + 1 for rank, (sid, _) in enumerate(sorted_by_total)}

    for sid in student_ids:
        scores, _ = exam_scores[sid]
        for subj in subjects:
            subj_scores = [(s, exam_scores[s][0][subj]) for s in student_ids]
            subj_sorted = sorted(subj_scores, key=lambda x: x[1], reverse=True)
            class_rank = next(i + 1 for i, (s, _) in enumerate(subj_sorted) if s == sid)

            cursor.execute(
                "INSERT INTO scores (student_id, exam_id, subject, score, class_rank, school_rank) VALUES (%s, %s, %s, %s, %s, %s)",
                (sid, exam_id, subj, scores[subj], class_rank, school_rank_map[sid])
            )

conn.commit()
cursor.close()
conn.close()
print("Done")
