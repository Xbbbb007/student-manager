package com.sms.entity;

public class Department {
    private Integer id;
    private String deptNo;
    private String deptName;

    public Department() {}

    public Department(Integer id, String deptNo, String deptName) {
        this.id = id;
        this.deptNo = deptNo;
        this.deptName = deptName;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getDeptNo() { return deptNo; }
    public void setDeptNo(String deptNo) { this.deptNo = deptNo; }

    public String getDeptName() { return deptName; }
    public void setDeptName(String deptName) { this.deptName = deptName; }

    @Override
    public String toString() {
        return "Department{" +
                "id=" + id +
                ", deptNo='" + deptNo + '\'' +
                ", deptName='" + deptName + '\'' +
                '}';
    }
}
