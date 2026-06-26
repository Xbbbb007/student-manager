package com.sms.dao.impl;

import com.sms.dao.LeaveRequestDAO;
import com.sms.entity.LeaveRequest;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class LeaveRequestDAOImpl implements LeaveRequestDAO {

    private final DBUtil.RowMapper<LeaveRequest> mapper = new DBUtil.RowMapper<LeaveRequest>() {
        @Override
        public LeaveRequest mapRow(ResultSet rs) throws SQLException {
            LeaveRequest lr = new LeaveRequest(
                    rs.getInt("id"),
                    rs.getInt("student_id"),
                    rs.getDate("start_date"),
                    rs.getDate("end_date"),
                    rs.getString("reason"),
                    rs.getString("status")
            );
            lr.setApproverId(rs.getInt("approver_id"));
            if (lr.getApproverId() == 0) {
                lr.setApproverId(null);
            }
            lr.setApproveTime(rs.getTimestamp("approve_time"));
            lr.setRemark(rs.getString("remark"));
            try {
                lr.setStudentNo(rs.getString("student_no"));
                lr.setStudentName(rs.getString("student_name"));
                lr.setClassName(rs.getString("class_name"));
            } catch (SQLException e) {
                // ignore
            }
            try {
                lr.setApproverName(rs.getString("approver_name"));
            } catch (SQLException e) {
                // ignore
            }
            return lr;
        }
    };

    private static final String BASE_SELECT = "SELECT lr.*, st.student_no, st.name as student_name, cl.class_name, " +
            "u.real_name as approver_name " +
            "FROM leave_request lr " +
            "JOIN student st ON lr.student_id = st.id " +
            "JOIN class cl ON st.class_id = cl.id " +
            "LEFT JOIN user u ON lr.approver_id = u.id ";

    @Override
    public LeaveRequest findById(Integer id) {
        try {
            return DBUtil.executeQueryOne(BASE_SELECT + "WHERE lr.id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(LeaveRequest request) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO leave_request (student_id, start_date, end_date, reason, status, approver_id, approve_time, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    request.getStudentId(), request.getStartDate(), request.getEndDate(), request.getReason(), request.getStatus(),
                    request.getApproverId(), request.getApproveTime(), request.getRemark());
            if (id > 0) {
                request.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(LeaveRequest request) {
        try {
            return DBUtil.executeUpdate("UPDATE leave_request SET student_id = ?, start_date = ?, end_date = ?, reason = ?, status = ?, approver_id = ?, approve_time = ?, remark = ? WHERE id = ?",
                    request.getStudentId(), request.getStartDate(), request.getEndDate(), request.getReason(), request.getStatus(),
                    request.getApproverId(), request.getApproveTime(), request.getRemark(), request.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM leave_request WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<LeaveRequest> findByStudentId(Integer studentId) {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "WHERE lr.student_id = ? ORDER BY lr.start_date DESC", mapper, studentId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<LeaveRequest> findPendingByTeacherId(Integer teacherId) {
        try {
            // Pending requests for students belonging to classes where the head teacher is this teacher!
            String sql = BASE_SELECT + "JOIN class c2 ON st.class_id = c2.id " +
                    "WHERE lr.status = '待审批' AND c2.head_teacher_id = ? ORDER BY lr.start_date ASC";
            return DBUtil.executeQuery(sql, mapper, teacherId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<LeaveRequest> findAll() {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "ORDER BY lr.start_date DESC", mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
