package com.sms.dao.impl;

import com.sms.dao.TeachingPlanDAO;
import com.sms.entity.TeachingPlan;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class TeachingPlanDAOImpl implements TeachingPlanDAO {

    private final DBUtil.RowMapper<TeachingPlan> mapper = new DBUtil.RowMapper<TeachingPlan>() {
        @Override
        public TeachingPlan mapRow(ResultSet rs) throws SQLException {
            TeachingPlan tp = new TeachingPlan(
                    rs.getInt("id"),
                    rs.getInt("course_id"),
                    rs.getInt("teacher_id"),
                    rs.getInt("class_id"),
                    rs.getString("semester"),
                    rs.getInt("max_students"),
                    rs.getInt("current_students")
            );
            if (tp.getClassId() == 0) {
                tp.setClassId(null);
            }
            try {
                tp.setCourseNo(rs.getString("course_no"));
                tp.setCourseName(rs.getString("course_name"));
                tp.setCourseType(rs.getString("type"));
                tp.setCourseCredit(rs.getDouble("credit"));
                tp.setTeacherNo(rs.getString("teacher_no"));
                tp.setTeacherName(rs.getString("teacher_name"));
            } catch (SQLException e) {
                // ignore if not joined
            }
            try {
                tp.setClassNo(rs.getString("class_no"));
                tp.setClassName(rs.getString("class_name"));
            } catch (SQLException e) {
                // ignore
            }
            return tp;
        }
    };

    private static final String BASE_SELECT = "SELECT tp.*, c.course_no, c.course_name, c.credit, c.type, " +
            "t.teacher_no, t.name as teacher_name, cl.class_no, cl.class_name " +
            "FROM teaching_plan tp " +
            "JOIN course c ON tp.course_id = c.id " +
            "JOIN teacher t ON tp.teacher_id = t.id " +
            "LEFT JOIN class cl ON tp.class_id = cl.id ";

    @Override
    public TeachingPlan findById(Integer id) {
        try {
            return DBUtil.executeQueryOne(BASE_SELECT + "WHERE tp.id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(TeachingPlan plan) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO teaching_plan (course_id, teacher_id, class_id, semester, max_students, current_students) VALUES (?, ?, ?, ?, ?, ?)",
                    plan.getCourseId(), plan.getTeacherId(), plan.getClassId(), plan.getSemester(), plan.getMaxStudents(), plan.getCurrentStudents());
            if (id > 0) {
                plan.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(TeachingPlan plan) {
        try {
            return DBUtil.executeUpdate("UPDATE teaching_plan SET course_id = ?, teacher_id = ?, class_id = ?, semester = ?, max_students = ?, current_students = ? WHERE id = ?",
                    plan.getCourseId(), plan.getTeacherId(), plan.getClassId(), plan.getSemester(), plan.getMaxStudents(), plan.getCurrentStudents(), plan.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM teaching_plan WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<TeachingPlan> findAll() {
        try {
            return DBUtil.executeQuery(BASE_SELECT, mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<TeachingPlan> findBySemester(String semester) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE tp.semester = ?", mapper, semester);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<TeachingPlan> findByClassId(Integer classId, String semester) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE tp.class_id = ? AND tp.semester = ?", mapper, classId, semester);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<TeachingPlan> findByTeacherId(Integer teacherId, String semester) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE tp.teacher_id = ? AND tp.semester = ?", mapper, teacherId, semester);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<TeachingPlan> findElectives(String semester) {
        try {
            // Elective courses do not have class_id bound in teaching_plan
            return DBUtil.executeQuery(BASE_SELECT + "WHERE tp.class_id IS NULL AND tp.semester = ?", mapper, semester);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
