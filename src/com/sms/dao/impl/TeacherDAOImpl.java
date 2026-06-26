package com.sms.dao.impl;

import com.sms.dao.TeacherDAO;
import com.sms.entity.Teacher;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class TeacherDAOImpl implements TeacherDAO {

    private final DBUtil.RowMapper<Teacher> mapper = new DBUtil.RowMapper<Teacher>() {
        @Override
        public Teacher mapRow(ResultSet rs) throws SQLException {
            Teacher t = new Teacher(
                    rs.getInt("id"),
                    rs.getInt("user_id"),
                    rs.getString("teacher_no"),
                    rs.getString("name"),
                    rs.getString("gender"),
                    rs.getString("phone"),
                    rs.getString("email"),
                    rs.getString("title"),
                    rs.getInt("department_id"),
                    rs.getInt("status")
            );
            t.setCreatedAt(rs.getTimestamp("created_at"));
            try {
                t.setDeptName(rs.getString("dept_name"));
            } catch (SQLException e) {
                // ignore
            }
            return t;
        }
    };

    @Override
    public Teacher findById(Integer id) {
        try {
            String sql = "SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.department_id = d.id WHERE t.id = ?";
            return DBUtil.executeQueryOne(sql, mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Teacher findByUserId(Integer userId) {
        try {
            String sql = "SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.department_id = d.id WHERE t.user_id = ?";
            return DBUtil.executeQueryOne(sql, mapper, userId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Teacher findByTeacherNo(String teacherNo) {
        try {
            String sql = "SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.department_id = d.id WHERE t.teacher_no = ?";
            return DBUtil.executeQueryOne(sql, mapper, teacherNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Teacher teacher) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO teacher (user_id, teacher_no, name, gender, phone, email, title, department_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    teacher.getUserId(), teacher.getTeacherNo(), teacher.getName(), teacher.getGender(),
                    teacher.getPhone(), teacher.getEmail(), teacher.getTitle(), teacher.getDepartmentId(), teacher.getStatus());
            if (id > 0) {
                teacher.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Teacher teacher) {
        try {
            return DBUtil.executeUpdate("UPDATE teacher SET user_id = ?, teacher_no = ?, name = ?, gender = ?, phone = ?, email = ?, title = ?, department_id = ?, status = ? WHERE id = ?",
                    teacher.getUserId(), teacher.getTeacherNo(), teacher.getName(), teacher.getGender(),
                    teacher.getPhone(), teacher.getEmail(), teacher.getTitle(), teacher.getDepartmentId(), teacher.getStatus(), teacher.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM teacher WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Teacher> findAll() {
        try {
            String sql = "SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.department_id = d.id";
            return DBUtil.executeQuery(sql, mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Teacher> findByDeptId(Integer deptId) {
        try {
            String sql = "SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.department_id = d.id WHERE t.department_id = ?";
            return DBUtil.executeQuery(sql, mapper, deptId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
