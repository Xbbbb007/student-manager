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
                    pool.add(createPhysicalConnection());
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
            for (Connection conn : pool) {
                try {
                    ((Connection) ((Proxy) conn).getClass().getInterfaces()[0].cast(conn)).close(); // Just close physically
                } catch (Exception e) {
                    // Ignore proxy closing issues, close actual connection if possible
                }
            }
            pool.clear();
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
