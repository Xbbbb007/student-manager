USE student_manager;

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    class_id INTEGER NOT NULL,
    exam_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    subject ENUM('chinese','math','english','science','ethics') NOT NULL,
    score FLOAT NOT NULL,
    class_rank INTEGER,
    school_rank INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (exam_id) REFERENCES exams(id),
    UNIQUE KEY uq_score (student_id, exam_id, subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
