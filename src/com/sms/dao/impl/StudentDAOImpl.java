package com.sms.dao.impl;

import com.sms.dao.StudentDAO;
import com.sms.entity.Student;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class StudentDAOImpl implements StudentDAO {

    private final DBUtil.RowMapper<Student> mapper = new DBUtil.RowMapper<Student>() {
        @Override
        public Student mapRow(ResultSet rs) throws SQLException {
            Student s = new Student(
                    rs.getInt("id"),
                    rs.getInt("user_id"),
                    rs.getString("student_no"),
                    rs.getString("name"),
                    rs.getString("gender"),
                    rs.getDate("birth_date"),
                    rs.getString("phone"),
                    rs.getString("email"),
                    rs.getString("address"),
                    rs.getDate("enroll_date"),
                    rs.getInt("class_id"),
                    rs.getString("photo_path"),
                    rs.getInt("status")
            );
            s.setCreatedAt(rs.getTimestamp("created_at"));
            try {
                s.setClassName(rs.getString("class_name"));
            } catch (SQLException e) {
                // ignore
            }
            try {
                s.setMajorName(rs.getString("major_name"));
            } catch (SQLException e) {
                // ignore
            }
            return s;
        }
    };

    @Override
    public Student findById(Integer id) {
        try {
            String sql = "SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id " +
                    "WHERE s.id = ?";
            return DBUtil.executeQueryOne(sql, mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Student findByUserId(Integer userId) {
        try {
            String sql = "SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id " +
                    "WHERE s.user_id = ?";
            return DBUtil.executeQueryOne(sql, mapper, userId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Student findByStudentNo(String studentNo) {
        try {
            String sql = "SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id " +
                    "WHERE s.student_no = ?";
            return DBUtil.executeQueryOne(sql, mapper, studentNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Student student) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO student (user_id, student_no, name, gender, birth_date, phone, email, address, enroll_date, class_id, photo_path, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    student.getUserId(), student.getStudentNo(), student.getName(), student.getGender(), student.getBirthDate(),
                    student.getPhone(), student.getEmail(), student.getAddress(), student.getEnrollDate(), student.getClassId(),
                    student.getPhotoPath(), student.getStatus());
            if (id > 0) {
                student.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Student student) {
        try {
            return DBUtil.executeUpdate("UPDATE student SET user_id = ?, student_no = ?, name = ?, gender = ?, birth_date = ?, phone = ?, email = ?, address = ?, enroll_date = ?, class_id = ?, photo_path = ?, status = ? WHERE id = ?",
                    student.getUserId(), student.getStudentNo(), student.getName(), student.getGender(), student.getBirthDate(),
                    student.getPhone(), student.getEmail(), student.getAddress(), student.getEnrollDate(), student.getClassId(),
                    student.getPhotoPath(), student.getStatus(), student.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM student WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Student> findAll() {
        try {
            String sql = "SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id";
            return DBUtil.executeQuery(sql, mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Student> findByClassId(Integer classId) {
        try {
            String sql = "SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id " +
                    "WHERE s.class_id = ?";
            return DBUtil.executeQuery(sql, mapper, classId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Student> searchStudents(String queryStr, Integer classId, Integer majorId, int offset, int limit) {
        try {
            List<Object> params = new ArrayList<>();
            StringBuilder sql = new StringBuilder("SELECT s.*, c.class_name, m.major_name FROM student s " +
                    "JOIN class c ON s.class_id = c.id " +
                    "JOIN major m ON c.major_id = m.id WHERE 1=1 ");

            if (queryStr != null && !queryStr.trim().isEmpty()) {
                sql.append("AND (s.student_no LIKE ? OR s.name LIKE ?) ");
                params.add("%" + queryStr + "%");
                params.add("%" + queryStr + "%");
            }
            if (classId != null) {
                sql.append("AND s.class_id = ? ");
                params.add(classId);
            }
            if (majorId != null) {
                sql.append("AND c.major_id = ? ");
                params.add(majorId);
            }

            sql.append("ORDER BY s.student_no LIMIT ? OFFSET ?");
            params.add(limit);
            params.add(offset);

            return DBUtil.executeQuery(sql.toString(), mapper, params.toArray());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int countStudents(String queryStr, Integer classId, Integer majorId) {
        try {
            List<Object> params = new ArrayList<>();
            StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM student s JOIN class c ON s.class_id = c.id WHERE 1=1 ");

            if (queryStr != null && !queryStr.trim().isEmpty()) {
                sql.append("AND (s.student_no LIKE ? OR s.name LIKE ?) ");
                params.add("%" + queryStr + "%");
                params.add("%" + queryStr + "%");
            }
            if (classId != null) {
                sql.append("AND s.class_id = ? ");
                params.add(classId);
            }
            if (majorId != null) {
                sql.append("AND c.major_id = ? ");
                params.add(majorId);
            }

            Integer count = DBUtil.executeQueryOne(sql.toString(), new DBUtil.RowMapper<Integer>() {
                @Override
                public Integer mapRow(ResultSet rs) throws SQLException {
                    return rs.getInt(1);
                }
            }, params.toArray());
            return count != null ? count : 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
