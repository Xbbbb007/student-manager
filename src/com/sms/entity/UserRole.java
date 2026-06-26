package com.sms.entity;

public enum UserRole {
    ADMIN, TEACHER, STUDENT;

    public static UserRole fromString(String val) {
        try {
            return UserRole.valueOf(val.toUpperCase());
        } catch (Exception e) {
            return null;
        }
    }
}
