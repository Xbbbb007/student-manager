SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS classes, students, staff, users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    password_plain VARCHAR(128) DEFAULT '',
    name VARCHAR(50) NOT NULL,
    role ENUM('teacher','admin') NOT NULL DEFAULT 'teacher',
    gender ENUM('male','female'),
    subject ENUM('chinese','math','english'),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    password_plain VARCHAR(128) DEFAULT '',
    name VARCHAR(50) NOT NULL,
    gender ENUM('male','female'),
    class_id INTEGER,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    section VARCHAR(20) NOT NULL DEFAULT '小学部',
    grade VARCHAR(20) NOT NULL,
    homeroom_teacher_id INTEGER,
    FOREIGN KEY (homeroom_teacher_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO staff (username, password_hash, password_plain, name, role) VALUES ('admin', '$2b$12$kBc7LgV/vwiydSy.V7bAdeKSFLZmYOA1ktva.LLLCK1WX4c6bvoy6', 'admin123', '系统管理员', 'admin');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('zhang_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '张老师', 'teacher', 'male', 'chinese');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('li_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '李老师', 'teacher', 'female', 'math');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('wang_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '王老师', 'teacher', 'female', 'english');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('zhao_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '赵老师', 'teacher', 'female', 'chinese');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('sun_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孙老师', 'teacher', 'male', 'math');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('qian_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '钱老师', 'teacher', 'male', 'english');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('chen_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '陈老师', 'teacher', 'female', 'chinese');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('yang_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '杨老师', 'teacher', 'male', 'math');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('liu_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '刘老师', 'teacher', 'female', 'english');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('huang_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '黄老师', 'teacher', 'male', 'chinese');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('zhou_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '周老师', 'teacher', 'female', 'math');
INSERT INTO staff (username, password_hash, password_plain, name, role, gender, subject) VALUES ('wu_laoshi', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '吴老师', 'teacher', 'male', 'english');
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (1, '小学部三年级一班', '小学部', '三年级', 1);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (2, '小学部三年级二班', '小学部', '三年级', 2);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (3, '小学部四年级一班', '小学部', '四年级', 3);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (4, '小学部四年级二班', '小学部', '四年级', 4);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (5, '初中部一年级一班', '初中部', '一年级', 5);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (6, '初中部一年级二班', '初中部', '一年级', 6);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (7, '初中部二年级一班', '初中部', '二年级', 7);
INSERT INTO classes (id, name, section, grade, homeroom_teacher_id) VALUES (8, '初中部二年级二班', '初中部', '二年级', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030101', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '葛浩然', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030102', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '高天阳', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030103', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '赵天宇', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030104', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '廖泽楷', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030105', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩景行', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030106', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '谢宇轩', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030107', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蔡子轩', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030108', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋致远', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030109', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '高文昊', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030110', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '何思远', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030111', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '魏俊哲', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030112', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蔡浩铭', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030113', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汤文昊', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030114', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '胡文博', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030115', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范致远', 'male', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030116', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '高梓萱', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030117', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '段芷晴', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030118', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邵雨桐', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030119', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孙悦然', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030120', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '金可欣', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030121', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '杨雅婷', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030122', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '程雨欣', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030123', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '胡梓涵', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030124', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁芷柔', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030125', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '潘欣怡', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030126', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋佳琪', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030127', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '唐语萱', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030128', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '夏梓萱', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030129', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范梓萌', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030130', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '方雅婷', 'female', 1);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030201', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '史思远', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030202', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '黄梓涵', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030203', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗天阳', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030204', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩宇轩', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030205', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '程子墨', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030206', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '魏浩然', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030207', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孟浩宇', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030208', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '石天阳', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030209', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩子骞', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030210', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汪宇轩', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030211', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾鹏飞', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030212', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '沈泽宇', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030213', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭子豪', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030214', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '戴景行', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030215', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹天阳', 'male', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030216', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '周婉晴', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030217', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '顾芷柔', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030218', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贺雨欣', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030219', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '冯芷晴', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030220', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '廖雅文', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030221', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '乔语嫣', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030222', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '沈梓涵', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030223', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '尹雨桐', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030224', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '张语萱', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030225', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹语嫣', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030226', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蒋梦洁', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030227', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '魏佳琪', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030228', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '熊雨桐', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030229', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '谭思涵', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01030230', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贾梦瑶', 'female', 2);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040101', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '武文博', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040102', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '胡博超', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040103', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '乔伟杰', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040104', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '冯文昊', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040105', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '何泽楷', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040106', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '刘子轩', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040107', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邓睿轩', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040108', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邓泽楷', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040109', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '廖文昊', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040110', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蔡梓涵', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040111', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '许泽楷', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040112', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋天宇', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040113', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋伟杰', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040114', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '程俊豪', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040115', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '唐文博', 'male', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040116', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范可欣', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040117', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孔芷晴', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040118', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余思涵', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040119', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '熊思琪', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040120', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '沈雨桐', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040121', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾梓萌', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040122', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '夏芷晴', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040123', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '陈雨桐', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040124', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩若曦', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040125', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孟可欣', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040126', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '许梦洁', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040127', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '胡雅静', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040128', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '朱芷晴', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040129', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '金婉晴', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040130', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邹婉晴', 'female', 3);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040201', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '龚子豪', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040202', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '林伟杰', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040203', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '金明远', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040204', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '熊子轩', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040205', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蒋睿泽', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040206', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '周子涵', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040207', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汪子豪', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040208', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗宇轩', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040209', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '姜浩铭', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040210', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '朱宇航', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040211', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '夏宇晨', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040212', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余浩宇', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040213', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贾博超', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040214', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '任俊杰', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040215', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '田子骞', 'male', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040216', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩雨桐', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040217', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蔡芷柔', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040218', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '史梓萱', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040219', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾梓涵', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040220', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汤梓萌', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040221', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁雅文', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040222', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '戴芷柔', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040223', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '龚悦然', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040224', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '侯梓萱', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040225', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '王子涵', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040226', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '廖梓萌', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040227', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '武思琪', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040228', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩可欣', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040229', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '苏思涵', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('01040230', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汪雅静', 'female', 4);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010101', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹景行', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010102', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '杨明远', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010103', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '姚天阳', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010104', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁思远', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010105', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '陆泽宇', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010106', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '唐文昊', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010107', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贾浩宇', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010108', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '顾宇航', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010109', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '吴俊杰', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010110', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭子骞', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010111', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '魏宇晨', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010112', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁宇晨', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010113', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '方泽楷', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010114', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹博文', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010115', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '段天宇', 'male', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010116', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '任梓涵', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010117', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '林静怡', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010118', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '李若曦', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010119', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭芷晴', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010120', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '廖雅婷', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010121', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '刘诗琪', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010122', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩梓萌', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010123', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗雨桐', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010124', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范语萱', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010125', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '赵梦瑶', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010126', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩梓萱', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010127', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贾佳琪', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010128', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邓可欣', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010129', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '田芷晴', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010130', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '陆可欣', 'female', 5);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010201', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邵宇晨', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010202', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '韩一鸣', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010203', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '方思远', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010204', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贺天宇', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010205', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邱泽宇', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010206', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '苏睿渊', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010207', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '叶昊天', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010208', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '沈子骞', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010209', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '乔景行', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010210', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范一鸣', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010211', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '雷梓涵', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010212', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孔浩然', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010213', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '石致远', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010214', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '白子涵', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010215', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '冯俊哲', 'male', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010216', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '苏雨桐', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010217', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '夏诗琪', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010218', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '徐欣怡', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010219', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '何思琪', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010220', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '葛悦然', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010221', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭思涵', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010222', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭语嫣', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010223', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '石思琪', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010224', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹雨桐', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010225', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '马可欣', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010226', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋雨彤', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010227', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '姜若曦', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010228', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邓思涵', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010229', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾芷晴', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02010230', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '叶雨彤', 'female', 6);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020101', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '潘泽宇', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020102', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '萧景行', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020103', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '尹博文', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020104', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邹伟杰', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020105', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '陈浩宇', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020106', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '徐子豪', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020107', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '彭思远', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020108', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗俊杰', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020109', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '龙泽宇', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020110', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '孙泽宇', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020111', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '谭泽楷', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020112', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '崔俊杰', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020113', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余致远', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020114', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范梓涵', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020115', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '侯俊豪', 'male', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020116', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余语嫣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020117', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '范诗琪', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020118', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '贾语嫣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020119', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '黄思琪', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020120', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曹可欣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020121', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁可欣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020122', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '崔静怡', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020123', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '沈雅静', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020124', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗雨欣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020125', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '宋语嫣', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020126', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '潘欣怡', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020127', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '唐雅静', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020128', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蔡静怡', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020129', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '苏思颖', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020130', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '冯梓萌', 'female', 7);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020201', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '梁嘉豪', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020202', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '谭浩铭', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020203', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '肖博超', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020204', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '苏睿渊', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020205', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '潘梓涵', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020206', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾伟杰', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020207', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '金浩铭', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020208', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '夏宇晨', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020209', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余天阳', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020210', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '郑天翔', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020211', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '蒋子涵', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020212', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '林景行', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020213', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '熊宇轩', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020214', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '曾浩宇', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020215', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '马浩然', 'male', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020216', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '高梓萌', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020217', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '罗芷晴', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020218', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '萧雅文', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020219', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '余思颖', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020220', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '何思涵', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020221', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '肖雨欣', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020222', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '龙语萱', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020223', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '魏思琪', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020224', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '乔佳琪', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020225', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '汪可欣', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020226', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '雷梓萌', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020227', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '白梓涵', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020228', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '吴思颖', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020229', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '林梦洁', 'female', 8);
INSERT INTO students (username, password_hash, password_plain, name, gender, class_id) VALUES ('02020230', '$2b$12$7Qkcmnvk0LQqx5509rqnmeOCEI84B03mQrTxL2dPf5c19hEjg2g.6', '123456', '邱梦洁', 'female', 8);