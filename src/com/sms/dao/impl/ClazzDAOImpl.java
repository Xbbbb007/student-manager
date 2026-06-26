package com.sms.dao.impl;

import com.sms.dao.ClazzDAO;
import com.sms.entity.Clazz;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class ClazzDAOImpl implements ClazzDAO {

    private final DBUtil.RowMapper<Clazz> mapper = new DBUtil.RowMapper<Clazz>() {
        @Override
        public Clazz mapRow(ResultSet rs) throws SQLException {
            Clazz c = new Clazz(
                    rs.getInt("id"),
                    rs.getString("class_no"),
                    rs.getString("class_name"),
                    rs.getInt("major_id"),
                    rs.getInt("enroll_year"),
                    rs.getInt("head_teacher_id")
            );
            if (c.getHeadTeacherId() == 0) {
                c.setHeadTeacherId(null);
            }
            try {
                c.setMajorName(rs.getString("major_name"));
            } catch (SQLException e) {
                // Ignore if not present
            }
            try {
                c.setHeadTeacherName(rs.getString("teacher_name"));
            } catch (SQLException e) {
                // Ignore if not present
            }
            return c;
        }
    };

    @Override
    public Clazz findById(Integer id) {
        try {
            String sql = "SELECT c.*, m.major_name, t.name as teacher_name FROM class c " +
                    "JOIN major m ON c.major_id = m.id " +
                    "LEFT JOIN teacher t ON c.head_teacher_id = t.id " +
                    "WHERE c.id = ?";
            return DBUtil.executeQueryOne(sql, mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Clazz findByClassNo(String classNo) {
        try {
            String sql = "SELECT c.*, m.major_name, t.name as teacher_name FROM class c " +
                    "JOIN major m ON c.major_id = m.id " +
                    "LEFT JOIN teacher t ON c.head_teacher_id = t.id " +
                    "WHERE c.class_no = ?";
            return DBUtil.executeQueryOne(sql, mapper, classNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Clazz clazz) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO class (class_no, class_name, major_id, enroll_year, head_teacher_id) VALUES (?, ?, ?, ?, ?)",
                    clazz.getClassNo(), clazz.getClassName(), clazz.getMajorId(), clazz.getEnrollYear(), clazz.getHeadTeacherId());
            if (id > 0) {
                clazz.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Clazz clazz) {
        try {
            return DBUtil.executeUpdate("UPDATE class SET class_no = ?, class_name = ?, major_id = ?, enroll_year = ?, head_teacher_id = ? WHERE id = ?",
                    clazz.getClassNo(), clazz.getClassName(), clazz.getMajorId(), clazz.getEnrollYear(), clazz.getHeadTeacherId(), clazz.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM class WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Clazz> findAll() {
        try {
            String sql = "SELECT c.*, m.major_name, t.name as teacher_name FROM class c " +
                    "JOIN major m ON c.major_id = m.id " +
                    "LEFT JOIN teacher t ON c.head_teacher_id = t.id";
            return DBUtil.executeQuery(sql, mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Clazz> findByMajorId(Integer majorId) {
        try {
            String sql = "SELECT c.*, m.major_name, t.name as teacher_name FROM class c " +
                    "JOIN major m ON c.major_id = m.id " +
                    "LEFT JOIN teacher t ON c.head_teacher_id = t.id " +
                    "WHERE c.major_id = ?";
            return DBUtil.executeQuery(sql, mapper, majorId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
