-- Seed data for studentsql_manage (minimal set)
USE studentsql_manage;

-- Departments
INSERT INTO department (dept_no, dept_name) VALUES
  ('CS','计算机科学与技术学院'),
  ('MATH','数学科学学院');

-- Majors
INSERT INTO major (major_no, major_name, dept_id, duration_years) VALUES
  ('CS01','计算机科学与技术',1,4),
  ('MATH01','应用数学',2,4);

-- Classes
INSERT INTO class (class_no, class_name, major_id, enroll_year, head_teacher_id) VALUES
  ('C2301','计算机2301班',1,2023,NULL),
  ('C2302','软件2301班',1,2023,NULL);

-- Admin user
INSERT INTO user (username, password_hash, salt, role, real_name, status) VALUES
  ('admin','d948d1acf15258835b23d7329add0e2b','salt123','ADMIN','系统管理员',1);

-- Teacher users (need user records first)
INSERT INTO user (username, password_hash, salt, role, real_name, status) VALUES
  ('teacher1','bc86e9fbd3c5ac12f5c3237b255034f8','salt456','TEACHER','王建国',1),
  ('teacher2','bc86e9fbd3c5ac12f5c3237b255034f8','salt456','TEACHER','刘秀英',1);

INSERT INTO teacher (user_id, teacher_no, name, gender, phone, email, title, department_id, status) VALUES
  (2,'T2001','王建国','男','13800010001','wangjg@school.edu.cn','教授',1,1),
  (3,'T2002','刘秀英','女','13800010002','liuxy@school.edu.cn','副教授',1,1);

-- Student users
INSERT INTO user (username, password_hash, salt, role, real_name, status) VALUES
  ('student1','b36e6fd615a046a6ff9b5ccf75036500','salt789','STUDENT','李明',1),
  ('student2','b36e6fd615a046a6ff9b5ccf75036500','salt789','STUDENT','张强',1);

INSERT INTO student (user_id, student_no, name, gender, birth_date, phone, email, address, enroll_date, class_id, status) VALUES
  (4,'S230101','李明','男','2005-05-12','13900010001','liming@school.edu.cn','北京', '2023-09-01',1,1),
  (5,'S230102','张强','男','2005-08-20','13900010002','zhangqiang@school.edu.cn','上海', '2023-09-01',1,1);
