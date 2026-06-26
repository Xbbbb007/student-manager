package com.sms.dao.impl;

import com.sms.dao.UserDAO;
import com.sms.entity.User;
import com.sms.entity.UserRole;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class UserDAOImpl implements UserDAO {

    private final DBUtil.RowMapper<User> mapper = new DBUtil.RowMapper<User>() {
        @Override
        public User mapRow(ResultSet rs) throws SQLException {
            User u = new User();
            u.setId(rs.getInt("id"));
            u.setUsername(rs.getString("username"));
            u.setPasswordHash(rs.getString("password_hash"));
            u.setSalt(rs.getString("salt"));
            u.setRole(UserRole.fromString(rs.getString("role")));
            u.setRealName(rs.getString("real_name"));
            u.setStatus(rs.getInt("status"));
            u.setFailedAttempts(rs.getInt("failed_attempts"));
            u.setLockUntil(rs.getTimestamp("lock_until"));
            u.setCreatedAt(rs.getTimestamp("created_at"));
            u.setUpdatedAt(rs.getTimestamp("updated_at"));
            return u;
        }
    };

    @Override
    public User findById(Integer id) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM user WHERE id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException("Error finding user by ID: " + id, e);
        }
    }

    @Override
    public User findByUsername(String username) {
        try {
            return DBUtil.executeQueryOne("SELECT * FROM user WHERE username = ?", mapper, username);
        } catch (SQLException e) {
            throw new RuntimeException("Error finding user by username: " + username, e);
        }
    }

    @Override
    public int insert(User user) {
        try {
            String sql = "INSERT INTO user (username, password_hash, salt, role, real_name, status, failed_attempts, lock_until) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
            int genId = DBUtil.executeInsert(sql,
                    user.getUsername(),
                    user.getPasswordHash(),
                    user.getSalt(),
                    user.getRole().name(),
                    user.getRealName(),
                    user.getStatus(),
                    user.getFailedAttempts() != null ? user.getFailedAttempts() : 0,
                    user.getLockUntil()
            );
            if (genId > 0) {
                user.setId(genId);
            }
            return genId > 0 ? 1 : 0;
        } catch (SQLException e) {
            throw new RuntimeException("Error inserting user: " + user.getUsername(), e);
        }
    }

    @Override
    public int update(User user) {
        try {
            String sql = "UPDATE user SET username = ?, password_hash = ?, salt = ?, role = ?, real_name = ?, status = ?, failed_attempts = ?, lock_until = ? WHERE id = ?";
            return DBUtil.executeUpdate(sql,
                    user.getUsername(),
                    user.getPasswordHash(),
                    user.getSalt(),
                    user.getRole().name(),
                    user.getRealName(),
                    user.getStatus(),
                    user.getFailedAttempts(),
                    user.getLockUntil(),
                    user.getId()
            );
        } catch (SQLException e) {
            throw new RuntimeException("Error updating user: " + user.getUsername(), e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM user WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException("Error deleting user with ID: " + id, e);
        }
    }

    @Override
    public List<User> findAll() {
        try {
            return DBUtil.executeQuery("SELECT * FROM user", mapper);
        } catch (SQLException e) {
            throw new RuntimeException("Error finding all users", e);
        }
    }
}
