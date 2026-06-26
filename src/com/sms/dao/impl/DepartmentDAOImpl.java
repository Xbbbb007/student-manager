package com.sms.dao.impl;

import com.sms.dao.DepartmentDAO;
import com.sms.entity.Department;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class DepartmentDAOImpl implements DepartmentDAO {

    private final DBUtil.RowMapper<Department> mapper = new DBUtil.RowMapper<Department>() {
        @Override
        public Department mapRow(ResultSet rs) throws SQLException {
            return new Department(
                    rs.getInt("id"),
                    rs.getString("dept_no"),
                    rs.getString("dept_name")
            );
        }
    };

    @Override
    public Department findById(Integer id) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM department WHERE id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Department findByDeptNo(String deptNo) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM department WHERE dept_no = ?", mapper, deptNo);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Department dept) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO department (dept_no, dept_name) VALUES (?, ?)",
                    dept.getDeptNo(), dept.getDeptName());
            if (id > 0) {
                dept.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Department dept) {
        try {
            return DBUtil.executeUpdate("UPDATE department SET dept_no = ?, dept_name = ? WHERE id = ?",
                    dept.getDeptNo(), dept.getDeptName(), dept.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM department WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Department> findAll() {
        try {
            return DBUtil.executeQuery("SELECT * FROM department", mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
