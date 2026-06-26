package com.sms.dao.impl;

import com.sms.dao.ScoreDAO;
import com.sms.entity.Score;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class ScoreDAOImpl implements ScoreDAO {

    private final DBUtil.RowMapper<Score> mapper = new DBUtil.RowMapper<Score>() {
        @Override
        public Score mapRow(ResultSet rs) throws SQLException {
            Score s = new Score(
                    rs.getInt("id"),
                    rs.getInt("teaching_plan_id"),
                    rs.getInt("student_id"),
                    rs.getObject("score") != null ? rs.getDouble("score") : null,
                    rs.getString("grade_level"),
                    rs.getString("exam_type")
            );
            s.setCreatedAt(rs.getTimestamp("created_at"));
            s.setUpdatedAt(rs.getTimestamp("updated_at"));
            try {
                s.setStudentNo(rs.getString("student_no"));
                s.setStudentName(rs.getString("student_name"));
                s.setClassName(rs.getString("class_name"));
                s.setCourseNo(rs.getString("course_no"));
                s.setCourseName(rs.getString("course_name"));
                s.setCourseCredit(rs.getDouble("credit"));
                s.setSemester(rs.getString("semester"));
            } catch (SQLException e) {
                // ignore
            }
            return s;
        }
    };

    private static final String BASE_SELECT = "SELECT s.*, st.student_no, st.name as student_name, cl.class_name, " +
            "c.course_no, c.course_name, c.credit, tp.semester " +
            "FROM score s " +
            "JOIN student st ON s.student_id = st.id " +
            "JOIN class cl ON st.class_id = cl.id " +
            "JOIN teaching_plan tp ON s.teaching_plan_id = tp.id " +
            "JOIN course c ON tp.course_id = c.id ";

    @Override
    public Score findById(Integer id) {
        try {
            return DBUtil.executeQueryOne(BASE_SELECT + "WHERE s.id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Score score) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO score (teaching_plan_id, student_id, score, grade_level, exam_type) VALUES (?, ?, ?, ?, ?)",
                    score.getTeachingPlanId(), score.getStudentId(), score.getScore(), score.getGradeLevel(), score.getExamType());
            if (id > 0) {
                score.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Score score) {
        try {
            return DBUtil.executeUpdate("UPDATE score SET score = ?, grade_level = ?, exam_type = ? WHERE id = ?",
                    score.getScore(), score.getGradeLevel(), score.getExamType(), score.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM score WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Score> findByStudentId(Integer studentId, String semester) {
        try {
            String sql = BASE_SELECT + "WHERE s.student_id = ? ";
            if (semester != null && !semester.isEmpty()) {
                sql += "AND tp.semester = ? ";
                return DBUtil.executeQuery(sql + "ORDER BY c.course_no, s.exam_type", mapper, studentId, semester);
            }
            return DBUtil.executeQuery(sql + "ORDER BY tp.semester, c.course_no, s.exam_type", mapper, studentId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Score> findByTeachingPlanId(Integer planId) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE s.teaching_plan_id = ? ORDER BY st.student_no, s.exam_type", mapper, planId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Score findByStudentAndPlanAndExamType(Integer studentId, Integer planId, String examType) {
        try {
            return DBUtil.executeQueryOne(BASE_SELECT + "WHERE s.student_id = ? AND s.teaching_plan_id = ? AND s.exam_type = ?", mapper, studentId, planId, examType);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Score> findByClassAndCourse(Integer classId, Integer courseId, String semester) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE tp.class_id = ? AND tp.course_id = ? AND tp.semester = ? ORDER BY st.student_no, s.exam_type", mapper, classId, courseId, semester);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
