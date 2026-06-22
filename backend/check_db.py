import sqlite3
conn = sqlite3.connect('app.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print('Tables:', tables)
for t in tables:
    if t == 'sqlite_sequence':
        continue
    c.execute(f'SELECT count(*) FROM "{t}"')
    print(f'  {t}: {c.fetchone()[0]}')
print('\n--- Students ---')
c.execute('SELECT id, username, name, class_id FROM students LIMIT 5')
for r in c.fetchall():
    print(r)
print('\n--- Classes ---')
c.execute('SELECT id, name, section, grade FROM classes LIMIT 10')
for r in c.fetchall():
    print(r)
print('\n--- Exams ---')
c.execute('SELECT id, name, class_id, exam_date FROM exams LIMIT 10')
for r in c.fetchall():
    print(r)
print('\n--- Scores sample ---')
c.execute('SELECT id, student_id, exam_id, subject, score, class_rank FROM scores LIMIT 10')
for r in c.fetchall():
    print(r)
conn.close()
