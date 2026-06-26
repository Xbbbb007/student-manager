import pymysql
import random
from datetime import datetime, timedelta

# Connect to the local MySQL db
conn = pymysql.connect(host='localhost', user='root', password='3274594297', db='student_manager')
cursor = conn.cursor()

# Get all student IDs and their classes
cursor.execute("SELECT id, class_id FROM students")
students = cursor.fetchall()
if not students:
    print("No students found. Please seed users/students first.")
    conn.close()
    exit(0)

# Clear old logs and requests
cursor.execute("DELETE FROM attendance")
cursor.execute("DELETE FROM leave_requests")

# Days range: past 10 school days
today = datetime.now()
dates = []
current_d = today - timedelta(days=15)
while current_d <= today:
    # school days only (Mon-Fri)
    if current_d.weekday() < 5:
        dates.append(current_d.date())
    current_d += timedelta(days=1)

print(f"Generating attendance logs for {len(students)} students over {len(dates)} days...")

# Attendance seeding
attendance_count = 0
for stu_id, class_id in students:
    # 90% Present, 5% Tardy, 3% Absent, 2% Leave
    for d in dates:
        for p in range(1, 9):  # 8 periods per day
            rand = random.random()
            if rand < 0.93:
                status = "present"
                reason = None
            elif rand < 0.97:
                status = "tardy"
                reason = "起晚了/交通拥堵" if random.random() < 0.5 else "课间活动迟到"
            else:
                status = "absent"
                reason = "无故缺勤"
            
            cursor.execute(
                """
                INSERT INTO attendance (student_id, class_id, date, period, status, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (stu_id, class_id, d, p, status, reason)
            )
            attendance_count += 1

# Seeding a few leave requests
cursor.execute("SELECT id FROM staff WHERE role = 'teacher' LIMIT 5")
teachers = [r[0] for r in cursor.fetchall()]

leave_count = 0
# Select 10 random students to have leave requests
for stu_id, class_id in random.sample(students, 10):
    start_d = today - timedelta(days=random.randint(1, 5))
    end_d = start_d + timedelta(days=random.randint(0, 2))
    
    reason = random.choice([
        "感冒发烧，需要去医院输液看病",
        "家里有急事，需要跟父母回老家一趟",
        "肚子疼，医生建议卧床休息一天",
        "参加市级少儿钢琴比赛，需请假半天"
    ])
    
    status = random.choice(["approved", "rejected", "pending"])
    approved_by = random.choice(teachers) if status != "pending" else None
    feedback = "同意请假，注意安全，回校后补上课程" if status == "approved" else ("不同意请假，原因说明不够详实" if status == "rejected" else None)
    
    cursor.execute(
        """
        INSERT INTO leave_requests (student_id, start_date, end_date, reason, status, approved_by, feedback)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (stu_id, start_d.date(), end_d.date(), reason, status, approved_by, feedback)
    )
    
    # If approved, write 'leave' status into attendance logs for these dates!
    if status == "approved":
        cursor.execute(
            """
            UPDATE attendance 
            SET status = 'leave', reason = '请假已批准' 
            WHERE student_id = %s AND date BETWEEN %s AND %s
            """,
            (stu_id, start_d.date(), end_d.date())
        )
        
    leave_count += 1

conn.commit()
cursor.close()
conn.close()

print(f"Successfully seeded {attendance_count} attendance records and {leave_count} leave requests!")
