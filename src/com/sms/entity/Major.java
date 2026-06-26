package com.sms.entity;

public class Major {
    private Integer id;
    private String majorNo;
    private String majorName;
    private Integer deptId;
    private Integer durationYears;
    
    // Joint fields (optional, for easier display)
    private String deptName;

    public Major() {}

    public Major(Integer id, String majorNo, String majorName, Integer deptId, Integer durationYears) {
        this.id = id;
        this.majorNo = majorNo;
        this.majorName = majorName;
        this.deptId = deptId;
        this.durationYears = durationYears;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getMajorNo() { return majorNo; }
    public void setMajorNo(String majorNo) { this.majorNo = majorNo; }

    public String getMajorName() { return majorName; }
    public void setMajorName(String majorName) { this.majorName = majorName; }

    public Integer getDeptId() { return deptId; }
    public void setDeptId(Integer deptId) { this.deptId = deptId; }

    public Integer getDurationYears() { return durationYears; }
    public void setDurationYears(Integer durationYears) { this.durationYears = durationYears; }

    public String getDeptName() { return deptName; }
    public void setDeptName(String deptName) { this.deptName = deptName; }

    @Override
    public String toString() {
        return "Major{" +
                "id=" + id +
                ", majorNo='" + majorNo + '\'' +
                ", majorName='" + majorName + '\'' +
                ", deptId=" + deptId +
                '}';
    }
}
