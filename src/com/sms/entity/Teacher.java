package com.sms.entity;

import java.sql.Timestamp;

public class Teacher {
    private Integer id;
    private Integer userId;
    private String teacherNo;
    private String name;
    private String gender;
    private String phone;
    private String email;
    private String title;
    private Integer departmentId;
    private Integer status; // 1: active, 0: left
    private Timestamp createdAt;

    // Joint fields for easier display
    private String deptName;

    public Teacher() {}

    public Teacher(Integer id, Integer userId, String teacherNo, String name, String gender, String phone, String email, String title, Integer departmentId, Integer status) {
        this.id = id;
        this.userId = userId;
        this.teacherNo = teacherNo;
        this.name = name;
        this.gender = gender;
        this.phone = phone;
        this.email = email;
        this.title = title;
        this.departmentId = departmentId;
        this.status = status;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public String getTeacherNo() { return teacherNo; }
    public void setTeacherNo(String teacherNo) { this.teacherNo = teacherNo; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Integer getDepartmentId() { return departmentId; }
    public void setDepartmentId(Integer departmentId) { this.departmentId = departmentId; }

    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    public String getDeptName() { return deptName; }
    public void setDeptName(String deptName) { this.deptName = deptName; }

    @Override
    public String toString() {
        return "Teacher{" +
                "id=" + id +
                ", teacherNo='" + teacherNo + '\'' +
                ", name='" + name + '\'' +
                ", title='" + title + '\'' +
                '}';
    }
}
