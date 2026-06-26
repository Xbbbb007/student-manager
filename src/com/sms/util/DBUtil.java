package com.sms.util;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class DBUtil {

    @FunctionalInterface
    public interface RowMapper<T> {
        T mapRow(ResultSet rs) throws SQLException;
    }

    public static Connection getConnection() throws SQLException {
        return SimpleConnectionPool.getInstance().getConnection();
    }

    public static void close(AutoCloseable... closeables) {
        if (closeables == null) return;
        for (AutoCloseable c : closeables) {
            if (c != null) {
                try {
                    c.close();
                } catch (Exception e) {
                    // Ignore
                }
            }
        }
    }

    public static int executeUpdate(String sql, Object... params) throws SQLException {
        try (Connection conn = getConnection()) {
            return executeUpdate(conn, sql, params);
        }
    }

    public static int executeUpdate(Connection conn, String sql, Object... params) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            setParameters(pstmt, params);
            return pstmt.executeUpdate();
        }
    }

    // Executes insert and returns generated auto-increment ID
    public static int executeInsert(String sql, Object... params) throws SQLException {
        try (Connection conn = getConnection()) {
            return executeInsert(conn, sql, params);
        }
    }

    public static int executeInsert(Connection conn, String sql, Object... params) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            setParameters(pstmt, params);
            int affected = pstmt.executeUpdate();
            if (affected > 0) {
                try (ResultSet rs = pstmt.getGeneratedKeys()) {
                    if (rs.next()) {
                        return rs.getInt(1);
                    }
                }
            }
            return -1;
        }
    }

    public static <T> List<T> executeQuery(String sql, RowMapper<T> mapper, Object... params) throws SQLException {
        try (Connection conn = getConnection()) {
            return executeQuery(conn, sql, mapper, params);
        }
    }

    public static <T> List<T> executeQuery(Connection conn, String sql, RowMapper<T> mapper, Object... params) throws SQLException {
        List<T> results = new ArrayList<>();
        PreparedStatement pstmt = null;
        ResultSet rs = null;
        try {
            pstmt = conn.prepareStatement(sql);
            setParameters(pstmt, params);
            rs = pstmt.executeQuery();
            while (rs.next()) {
                results.add(mapper.mapRow(rs));
            }
        } finally {
            close(rs, pstmt);
        }
        return results;
    }

    public static <T> T executeQueryOne(String sql, RowMapper<T> mapper, Object... params) throws SQLException {
        List<T> list = executeQuery(sql, mapper, params);
        return list.isEmpty() ? null : list.get(0);
    }

    public static <T> T executeQueryOne(Connection conn, String sql, RowMapper<T> mapper, Object... params) throws SQLException {
        List<T> list = executeQuery(conn, sql, mapper, params);
        return list.isEmpty() ? null : list.get(0);
    }

    private static void setParameters(PreparedStatement pstmt, Object... params) throws SQLException {
        if (params == null) return;
        for (int i = 0; i < params.length; i++) {
            pstmt.setObject(i + 1, params[i]);
        }
    }
}
