package com.sms.util;

import java.io.FileInputStream;
import java.io.InputStream;
import java.io.PrintWriter;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.util.LinkedList;
import java.util.Properties;
import java.util.logging.Logger;
import javax.sql.DataSource;

public class SimpleConnectionPool implements DataSource {

    private static SimpleConnectionPool instance;
    private final String url;
    private final String username;
    private final String password;
    private final int initialSize;
    private final int maxActive;
    private final long maxWait;

    private final LinkedList<Connection> pool = new LinkedList<>();
    private final LinkedList<Connection> physicalConnections = new LinkedList<>(); // Bug #6: track physical connections for proper shutdown
    private int activeCount = 0;

    private SimpleConnectionPool() {
        try {
            Properties props = new Properties();
            try (InputStream in = new FileInputStream("config/db.properties")) {
                props.load(in);
            }
            this.url = props.getProperty("db.url");
            this.username = props.getProperty("db.username");
            this.password = props.getProperty("db.password");
            this.initialSize = Integer.parseInt(props.getProperty("db.initialSize", "5"));
            this.maxActive = Integer.parseInt(props.getProperty("db.maxActive", "10"));
            this.maxWait = Long.parseLong(props.getProperty("db.maxWait", "3000"));

            // Load MySQL Driver
            try {
                Class.forName("com.mysql.cj.jdbc.Driver");
            } catch (ClassNotFoundException e) {
                // Fallback to older driver just in case
                Class.forName("com.mysql.jdbc.Driver");
            }

            // Pre-fill pool
            synchronized (pool) {
                for (int i = 0; i < initialSize; i++) {
                    Connection c = createPhysicalConnection();
                    pool.add(c);
                    physicalConnections.add(c);
                }
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize Connection Pool", e);
        }
    }

    public static synchronized SimpleConnectionPool getInstance() {
        if (instance == null) {
            instance = new SimpleConnectionPool();
        }
        return instance;
    }

    private Connection createPhysicalConnection() throws SQLException {
        return DriverManager.getConnection(url, username, password);
    }

    @Override
    public Connection getConnection() throws SQLException {
        synchronized (pool) {
            long startTime = System.currentTimeMillis();
            while (pool.isEmpty()) {
                if (activeCount < maxActive) {
                    Connection conn = createPhysicalConnection();
                    physicalConnections.add(conn); // track it
                    activeCount++;
                    return wrapConnection(conn);
                } else {
                    long elapsed = System.currentTimeMillis() - startTime;
                    long waitRemaining = maxWait - elapsed;
                    if (waitRemaining <= 0) {
                        throw new SQLException("Connection pool timeout: no available connections");
                    }
                    try {
                        pool.wait(waitRemaining);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        throw new SQLException("Connection request interrupted", e);
                    }
                }
            }
            Connection conn = pool.removeFirst();
            // Bug #7 修复：检查连接有效性，防止 MySQL wait_timeout 超时后报 "Communications link failure"
            try {
                if (!conn.isValid(2)) {
                    // 连接已断开，丢弃并新建
                    try { conn.close(); } catch (Exception ignored) {}
                    conn = createPhysicalConnection();
                }
            } catch (SQLException e) {
                try { conn.close(); } catch (Exception ignored) {}
                conn = createPhysicalConnection();
            }
            activeCount++;
            return wrapConnection(conn);
        }
    }

    private Connection wrapConnection(final Connection physicalConn) {
        return (Connection) Proxy.newProxyInstance(
                SimpleConnectionPool.class.getClassLoader(),
                new Class<?>[]{Connection.class},
                new InvocationHandler() {
                    @Override
                    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                        if ("close".equals(method.getName())) {
                            returnConnection(physicalConn);
                            return null;
                        }
                        try {
                            return method.invoke(physicalConn, args);
                        } catch (Exception e) {
                            // Unwrap TargetException
                            if (e.getCause() != null) {
                                throw e.getCause();
                            }
                            throw e;
                        }
                    }
                }
        );
    }

    private void returnConnection(Connection conn) {
        synchronized (pool) {
            try {
                // Ensure connection is not closed and is in a clean state (commit any pending changes)
                if (conn.isClosed()) {
                    activeCount--;
                    pool.add(createPhysicalConnection());
                } else {
                    if (!conn.getAutoCommit()) {
                        conn.setAutoCommit(true);
                    }
                    pool.addLast(conn);
                    activeCount--;
                }
            } catch (SQLException e) {
                // If checking fails, discard connection and create a new one
                activeCount--;
                try {
                    pool.addLast(createPhysicalConnection());
                } catch (SQLException ex) {
                    // Ignore
                }
            }
            pool.notifyAll();
        }
    }

    public synchronized void shutdown() {
        synchronized (pool) {
            // Bug #6 修复：直接关闭物理连接，而非代理（代理的 close() 会被拦截到 returnConnection）
            for (Connection physical : physicalConnections) {
                try {
                    if (!physical.isClosed()) {
                        physical.close();
                    }
                } catch (Exception e) {
                    // Ignore individual close errors
                }
            }
            physicalConnections.clear();
            pool.clear();
            activeCount = 0;
        }
    }

    @Override
    public Connection getConnection(String username, String password) throws SQLException {
        throw new UnsupportedOperationException("Not supported");
    }

    @Override
    public PrintWriter getLogWriter() throws SQLException {
        return DriverManager.getLogWriter();
    }

    @Override
    public void setLogWriter(PrintWriter out) throws SQLException {
        DriverManager.setLogWriter(out);
    }

    @Override
    public void setLoginTimeout(int seconds) throws SQLException {
        DriverManager.setLoginTimeout(seconds);
    }

    @Override
    public int getLoginTimeout() throws SQLException {
        return DriverManager.getLoginTimeout();
    }

    @Override
    public Logger getParentLogger() throws SQLFeatureNotSupportedException {
        throw new SQLFeatureNotSupportedException();
    }

    @Override
    public <T> T unwrap(Class<T> iface) throws SQLException {
        throw new SQLException("Not a wrapper");
    }

    @Override
    public boolean isWrapperFor(Class<?> iface) throws SQLException {
        return false;
    }
}
