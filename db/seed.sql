USE student_manager_db;

-- 1. user 用户表数据
-- 密码明文：admin -> admin123, teacher -> teacher123, student -> student123
INSERT INTO user (id, username, password_hash, salt, role, real_name, status) VALUES
(1, 'admin', 'd948d1acf15258835b23d7329add0e2b', 'salt123', 'ADMIN', '系统管理员', 1),
(2, 'teacher1', 'bc86e9fbd3c5ac12f5c3237b255034f8', 'salt456', 'TEACHER', '王建国', 1),
(3, 'teacher2', 'bc86e9fbd3c5ac12f5c3237b255034f8', 'salt456', 'TEACHER', '刘秀英', 1),
(4, 'teacher3', 'bc86e9fbd3c5ac12f5c3237b255034f8', 'salt456', 'TEACHER', '张爱华', 1),
(5, 'student1', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '李明', 1),
(6, 'student2', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '张强', 1),
(7, 'student3', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '王芳', 1),
(8, 'student4', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '赵敏', 1),
(9, 'student5', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '陈龙', 1),
(10, 'student6', 'b36e6fd615a046a6ff9b5ccf75036500', 'salt789', 'STUDENT', '徐静', 1);

-- 2. department 院系表数据
INSERT INTO department (id, dept_no, dept_name) VALUES
(1, 'CS', '计算机科学与技术学院'),
(2, 'EE', '电子信息工程学院'),
(3, 'MATH', '数学科学学院');

-- 3. major 专业表数据
INSERT INTO major (id, major_no, major_name, dept_id, duration_years) VALUES
(1, 'CS01', '计算机科学与技术', 1, 4),
(2, 'SE02', '软件工程', 1, 4),
(3, 'EE01', '电子信息工程', 2, 4),
(4, 'MA01', '应用数学', 3, 4);

-- 4. teacher 教师表数据
INSERT INTO teacher (id, user_id, teacher_no, name, gender, phone, email, title, department_id, status) VALUES
(1, 2, 'T2001', '王建国', '男', '13800010001', 'wangjg@school.edu.cn', '教授', 1, 1),
(2, 3, 'T2002', '刘秀英', '女', '13800010002', 'liuxy@school.edu.cn', '副教授', 1, 1),
(3, 4, 'T2003', '张爱华', '女', '13800010003', 'zhangah@school.edu.cn', '讲师', 3, 1);

-- 5. class 班级表数据
INSERT INTO class (id, class_no, class_name, major_id, enroll_year, head_teacher_id) VALUES
(1, 'C2301', '计算机2301班', 1, 2023, 1),
(2, 'C2302', '软件2301班', 2, 2023, 2);

-- 6. student 学生表数据
INSERT INTO student (id, user_id, student_no, name, gender, birth_date, phone, email, address, enroll_date, class_id, status) VALUES
(1, 5, 'S230101', '李明', '男', '2005-05-12', '13900010001', 'liming@school.edu.cn', '北京市朝阳区', '2023-09-01', 1, 1),
(2, 6, 'S230102', '张强', '男', '2005-08-20', '13900010002', 'zhangqiang@school.edu.cn', '上海市浦东新区', '2023-09-01', 1, 1),
(3, 7, 'S230103', '王芳', '女', '2005-02-15', '13900010003', 'wangfang@school.edu.cn', '广州市天河区', '2023-09-01', 1, 1),
(4, 8, 'S230201', '赵敏', '女', '2005-11-30', '13900010004', 'zhaomin@school.edu.cn', '深圳市南山区', '2023-09-01', 2, 1),
(5, 9, 'S230202', '陈龙', '男', '2005-04-05', '13900010005', 'chenlong@school.edu.cn', '杭州市西湖区', '2023-09-01', 2, 1),
(6, 10, 'S230203', '徐静', '女', '2005-09-18', '13900010006', 'xujing@school.edu.cn', '成都市武侯区', '2023-09-01', 2, 1);

-- 7. course 课程表数据
INSERT INTO course (id, course_no, course_name, credit, hours, type) VALUES
(1, 'CO101', '高等数学', 5.0, 80, '必修'),
(2, 'CO102', 'Java程序设计', 4.0, 64, '必修'),
(3, 'CO103', '数据库系统原理', 3.5, 56, '必修'),
(4, 'CO104', '面向对象课程设计', 2.0, 32, '选修'),
(5, 'CO105', '音乐欣赏', 1.5, 24, '公选');

-- 8. teaching_plan 教学计划表数据 (定义"谁在哪个学期教哪个班的哪门课")
INSERT INTO teaching_plan (id, course_id, teacher_id, class_id, semester, max_students, current_students) VALUES
-- 必修课
(1, 1, 3, 1, '2025-2026-1', 60, 3), -- 高等数学，张爱华，计算机2301
(2, 2, 1, 1, '2025-2026-1', 60, 3), -- Java程序设计，王建国，计算机2301
(3, 3, 2, 2, '2025-2026-1', 60, 3), -- 数据库系统原理，刘秀英，软件2301
-- 选修课 (选修课class_id可为空)
(4, 4, 1, NULL, '2025-2026-1', 30, 3), -- 面向对象课程设计，王建国，选课模式
(5, 5, 2, NULL, '2025-2026-1', 50, 4); -- 音乐欣赏，刘秀英，选课模式

-- 9. score 成绩表数据
-- 必修课 高等数学 成绩录入
INSERT INTO score (teaching_plan_id, student_id, score, grade_level, exam_type) VALUES
(1, 1, 85.0, 'B', '期末'),
(1, 2, 92.0, 'A', '期末'),
(1, 3, 58.0, 'F', '期末'),
-- 必修课 Java程序设计 成绩录入
(2, 1, 95.0, 'A', '期末'),
(2, 2, 88.0, 'B', '期末'),
(2, 3, 76.0, 'C', '期末'),
-- 必修课 数据库系统原理 成绩录入
(3, 4, 82.0, 'B', '期末'),
(3, 5, 68.0, 'D', '期末'),
(3, 6, 91.0, 'A', '期末'),
-- 选修课 面向对象课程设计 选课及成绩录入 (学生1, 2, 3 选了这门课)
(4, 1, 89.0, 'B', '期末'),
(4, 2, 94.0, 'A', '期末'),
(4, 3, NULL, NULL, '期末'), -- 学生3尚未录入成绩
-- 公选课 音乐欣赏 选课及成绩录入 (学生1, 3, 4, 6 选了这门课)
(5, 1, 90.0, 'A', '期末'),
(5, 3, 85.0, 'B', '期末'),
(5, 4, 73.0, 'C', '期末'),
(5, 6, NULL, NULL, '期末'); -- 学生6尚未录入成绩

-- 10. attendance 考勤表数据
INSERT INTO attendance (student_id, teaching_plan_id, attend_date, status, remark) VALUES
(1, 2, '2026-03-02', '出勤', 'Java上课点名'),
(2, 2, '2026-03-02', '出勤', 'Java上课点名'),
(3, 2, '2026-03-02', '迟到', '迟到5分钟'),
(1, 2, '2026-03-09', '出勤', 'Java上课点名'),
(2, 2, '2026-03-09', '旷课', '无故未到'),
(3, 2, '2026-03-09', '请假', '病假，有假条');

-- 11. schedule 课表表数据
INSERT INTO schedule (teaching_plan_id, day_of_week, section_start, section_end, classroom, campus) VALUES
(1, 1, 1, 2, '教三-301', '主校区'), -- 高等数学: 周一 1-2 节
(1, 3, 1, 2, '教三-301', '主校区'), -- 高等数学: 周三 1-2 节
(2, 2, 3, 4, '机房-502', '主校区'), -- Java: 周二 3-4 节
(2, 4, 3, 4, '机房-502', '主校区'), -- Java: 周四 3-4 节
(3, 1, 3, 4, '教四-201', '主校区'), -- 数据库: 周一 3-4 节
(3, 4, 1, 2, '教四-201', '主校区'), -- 数据库: 周四 1-2 节
(4, 5, 5, 8, '机房-504', '主校区'), -- 面向对象设计: 周五 5-8 节
(5, 3, 7, 8, '多媒体-104', '东校区'); -- 音乐欣赏: 周三 7-8 节

-- 12. notice 公告表数据
INSERT INTO notice (title, content, publisher_id, target_role, is_top) VALUES
('关于2026年春季学期开学注册的通知', '请全体学生于3月1日前登录系统完成注册并到班主任处报到。', 1, 'ALL', 1),
('关于提交Java课程设计中期报告的通知', '请计算机2301班同学在下周五前将Java课程设计中期报告提交至王老师信箱。', 2, 'STUDENT', 0),
('关于教师教学质量评价的通知', '各位教师请在第16周完成教学自评及同行互评工作。', 1, 'TEACHER', 0);

-- 13. leave_request 请假申请表数据
INSERT INTO leave_request (student_id, start_date, end_date, reason, status, approver_id, approve_time, remark) VALUES
(3, '2026-03-09', '2026-03-09', '身体不适，需要去医院看病', '已批准', 2, '2026-03-08 18:30:00', '批准，注意安全，事后补假条'),
(1, '2026-04-12', '2026-04-14', '家里有急事，需要回家处理', '待审批', NULL, NULL, NULL);
