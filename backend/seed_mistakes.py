import pymysql
import random
from datetime import datetime, timedelta

# Connect to the local MySQL db
conn = pymysql.connect(host='localhost', user='root', password='123456', db='student_manager')
cursor = conn.cursor()

# Get some student IDs
cursor.execute("SELECT id, name FROM students LIMIT 15")
students = cursor.fetchall()
if not students:
    print("No students found. Please seed users/students first.")
    conn.close()
    exit(0)

# Subjects
subjects = ['chinese', 'math', 'english', 'science', 'ethics']

# Some dummy questions and answers
mistakes_pool = {
    'chinese': [
        ("指出下列词语中字形完全正确的一项是哪一个？", "我的错解：A选项（包含了错别字‘提纲携领’）", "正确解答：B选项。A项中的‘提纲携领’应为‘提纲挈领’，属于形近字错误。"),
        ("解释文言文《出师表》中‘先帝不以臣卑鄙’的‘卑鄙’意思。", "我的错解：卑劣下流，道德败坏。", "正确解答：身份低微，见识短浅。在古代汉语中，‘卑’指地位低下，‘鄙’指见识短浅，属词义消长与演变。"),
        ("默写古诗词《钱塘湖春行》中描写莺燕的句子。", "我的错解：几处早莺争暖树，谁家新燕喙春泥。", "正确解答：几处早莺争暖树，谁家新燕啄春泥。注意‘啄’字字形，不要写成‘喙’或‘琢’。")
    ],
    'math': [
        ("已知函数 f(x) = x^2 - 2ax + 3 在区间 [1, 2] 上单调递减，求实数 a 的取值范围。", "我的错解：a < 1 或者是对称轴 x = a < 1。", "正确解答：a >= 2。因为对称轴为 x = a，要使二次函数在 [1, 2] 上单调递减，需使得整个区间 [1, 2] 都在对称轴左侧，即 a >= 2。"),
        ("计算下列定积分：∫(0 to 1) (x^2 + 1) dx。", "我的错解：1/2 + 1 = 1.5。", "正确解答：4/3。原函数为 x^3/3 + x，代入上限1和下限0，得到 (1/3 + 1) - 0 = 4/3。"),
        ("在等差数列 {an} 中，若 a1 + a5 = 10，则 a3 的值等于多少？", "我的错解：由于不知公差，无法求解。", "正确解答：a3 = 5。利用等差中项性质，a1 + a5 = 2*a3 = 10，因此 a3 = 5。")
    ],
    'english': [
        ("Complete the sentence: By the time we arrived at the cinema, the movie ______ (start).", "我的错解：started", "正确解答：had started. By the time 引导的时间状语从句表示过去的时间，主句动作发生在此过去时间之前，故使用过去完成时。"),
        ("下列单词中划线部分发音不同的一项是？", "我的错解：C项（认为head中ea发音为/i:/）", "正确解答：A项。great /greit/, head /hed/, bread /bred/，划线部分为ea，great的发音与众不同。"),
        ("Explain the difference between 'affect' and 'effect'.", "我的错解：两个词都是动词，可以互换使用。", "正确解答：affect主要用作动词，意思是“影响”；effect主要用作名词，意思是“效果”、“影响”。")
    ],
    'science': [
        ("为什么水在加热到100摄氏度时会沸腾？沸腾的过程中温度会变化吗？", "我的错解：沸腾过程中温度继续升高，直到水全部蒸发完。", "正确解答：在标准大气压下，水的沸点是100℃。水在沸腾时，虽然继续吸收热量，但温度保持100℃不变。"),
        ("简述光合作用的化学方程式及能量转换过程。", "我的错解：二氧化碳 + 水 -> 淀粉，放出氧气，能量没有变。", "正确解答：二氧化碳 + 水 —(光能/叶绿体)—> 有机物(储存着化学能) + 氧气。光能转换为了化学能储存起来。")
    ],
    'ethics': [
        ("什么是宪法？为什么宪法是我国的根本大法？", "我的错解：宪法是规定普通公民行为准则的法律，跟其他法律一样。", "正确解答：宪法是国家的根本大法，规定国家根本制度和根本任务，具有最高的法律效力。普通法律必须依据宪法制定，不得与宪法相抵触。")
    ]
}

# Clear old mistakes
cursor.execute("DELETE FROM mistakes")

# Seed random mistakes
count = 0
for stu_id, stu_name in students:
    # Each student gets 3-6 random mistakes
    num_mistakes = random.randint(3, 6)
    chosen_subjects = random.sample(subjects, random.randint(2, 4))
    
    for subj in chosen_subjects:
        pool = mistakes_pool.get(subj, [])
        if not pool:
            continue
        
        q, my, corr = random.choice(pool)
        is_mastered = random.choice([True, False])
        
        # Create a random date within the last 15 days
        days_ago = random.randint(1, 15)
        created_at = datetime.now() - timedelta(days=days_ago)
        created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            """
            INSERT INTO mistakes (student_id, subject, question_desc, my_answer, correct_answer, is_mastered, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (stu_id, subj, q, my, corr, is_mastered, created_at_str)
        )
        count += 1

conn.commit()
cursor.close()
conn.close()

print(f"Successfully seeded {count} mistakes for {len(students)} students!")
