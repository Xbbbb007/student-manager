package com.sms.dao.impl;

import com.sms.dao.CourseDAO;
import com.sms.entity.Course;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class CourseDAOImpl implements CourseDAO {

    private final DBUtil.RowMapper<Course> mapper = new DBUtil.RowMapper<Course>() {
        @Override
        public Course mapRow(ResultSet rs) throws SQLException {
            return new Course(
                    rs.getInt("id"),
                    rs.getString("course_no"),
                    rs.getString("course_name"),
                    rs.getDouble("credit"),
                    rs.getInt("hours"),
                    rs.getString("type")
            );
        }
    };

    @Override
    public Course findById(Integer id) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM course WHERE id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Course findByCourseNo(String courseNo) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM course WHERE course_no = ?", mapper, courseNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Course course) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO course (course_no, course_name, credit, hours, type) VALUES (?, ?, ?, ?, ?)",
                    course.getCourseNo(), course.getCourseName(), course.getCredit(), course.getHours(), course.getType());
            if (id > 0) {
                course.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Course course) {
        try {
            return DBUtil.executeUpdate("UPDATE course SET course_no = ?, course_name = ?, credit = ?, hours = ?, type = ? WHERE id = ?",
                    course.getCourseNo(), course.getCourseName(), course.getCredit(), course.getHours(), course.getType(), course.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM course WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Course> findAll() {
        try {
            return DBUtil.executeQuery("SELECT * FROM course", mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
