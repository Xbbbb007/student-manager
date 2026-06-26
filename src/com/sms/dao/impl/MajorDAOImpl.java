package com.sms.dao.impl;

import com.sms.dao.MajorDAO;
import com.sms.entity.Major;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class MajorDAOImpl implements MajorDAO {

    private final DBUtil.RowMapper<Major> mapper = new DBUtil.RowMapper<Major>() {
        @Override
        public Major mapRow(ResultSet rs) throws SQLException {
            Major m = new Major(
                    rs.getInt("id"),
                    rs.getString("major_no"),
                    rs.getString("major_name"),
                    rs.getInt("dept_id"),
                    rs.getInt("duration_years")
            );
            try {
                // If query has department join
                m.setDeptName(rs.getString("dept_name"));
            } catch (SQLException e) {
                // Ignore if column doesn't exist
            }
            return m;
        }
    };

    @Override
    public Major findById(Integer id) {
        try {
            String sql = "SELECT m.*, d.dept_name FROM major m JOIN department d ON m.dept_id = d.id WHERE m.id = ?";
            return DBUtil.executeQueryOne(sql, mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Major findByMajorNo(String majorNo) {
        try {
            String sql = "SELECT m.*, d.dept_name FROM major m JOIN department d ON m.dept_id = d.id WHERE m.major_no = ?";
            return DBUtil.executeQueryOne(sql, mapper, majorNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Major major) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO major (major_no, major_name, dept_id, duration_years) VALUES (?, ?, ?, ?)",
                    major.getMajorNo(), major.getMajorName(), major.getDeptId(), major.getDurationYears());
            if (id > 0) {
                major.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Major major) {
        try {
            return DBUtil.executeUpdate("UPDATE major SET major_no = ?, major_name = ?, dept_id = ?, duration_years = ? WHERE id = ?",
                    major.getMajorNo(), major.getMajorName(), major.getDeptId(), major.getDurationYears(), major.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM major WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Major> findAll() {
        try {
            String sql = "SELECT m.*, d.dept_name FROM major m JOIN department d ON m.dept_id = d.id";
            return DBUtil.executeQuery(sql, mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Major> findByDeptId(Integer deptId) {
        try {
            String sql = "SELECT m.*, d.dept_name FROM major m JOIN department d ON m.dept_id = d.id WHERE m.dept_id = ?";
            return DBUtil.executeQuery(sql, mapper, deptId);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
