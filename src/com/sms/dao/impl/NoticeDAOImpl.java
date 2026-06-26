package com.sms.dao.impl;

import com.sms.dao.NoticeDAO;
import com.sms.entity.Notice;
import com.sms.util.DBUtil;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public class NoticeDAOImpl implements NoticeDAO {

    private final DBUtil.RowMapper<Notice> mapper = new DBUtil.RowMapper<Notice>() {
        @Override
        public Notice mapRow(ResultSet rs) throws SQLException {
            Notice n = new Notice(
                    rs.getInt("id"),
                    rs.getString("title"),
                    rs.getString("content"),
                    rs.getInt("publisher_id"),
                    rs.getString("target_role"),
                    rs.getInt("is_top"),
                    rs.getInt("status")
            );
            n.setCreatedAt(rs.getTimestamp("created_at"));
            try {
                n.setPublisherName(rs.getString("publisher_name"));
            } catch (SQLException e) {
                // ignore
            }
            return n;
        }
    };

    private static final String BASE_SELECT = "SELECT n.*, u.real_name as publisher_name " +
            "FROM notice n " +
            "JOIN user u ON n.publisher_id = u.id ";

    @Override
    public Notice findById(Integer id) {
        try {
            return DBUtil.executeQueryOne(BASE_SELECT + "WHERE n.id = ?", mapper, id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int insert(Notice notice) {
        try {
            int id = DBUtil.executeInsert("INSERT INTO notice (title, content, publisher_id, target_role, is_top, status) VALUES (?, ?, ?, ?, ?, ?)",
                    notice.getTitle(), notice.getContent(), notice.getPublisherId(), notice.getTargetRole(), notice.getIsTop(), notice.getStatus());
            if (id > 0) {
                notice.setId(id);
                return 1;
            }
            return 0;
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int update(Notice notice) {
        try {
            return DBUtil.executeUpdate("UPDATE notice SET title = ?, content = ?, target_role = ?, is_top = ?, status = ? WHERE id = ?",
                    notice.getTitle(), notice.getContent(), notice.getTargetRole(), notice.getIsTop(), notice.getStatus(), notice.getId());
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public int deleteById(Integer id) {
        try {
            return DBUtil.executeUpdate("DELETE FROM notice WHERE id = ?", id);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Notice> findByRole(String targetRole) {
        try {
            // Target role can see notices targetted to ALL or to their specific role, and only status=1 (normal, not recalled)
            String sql = BASE_SELECT + "WHERE n.status = 1 AND (n.target_role = 'ALL' OR n.target_role = ?) ORDER BY n.is_top DESC, n.created_at DESC";
            return DBUtil.executeQuery(sql, mapper, targetRole);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Notice> findAll() {
        try {
            return DBUtil.executeQuery(BASE_SELECT + "ORDER BY n.is_top DESC, n.created_at DESC", mapper);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
