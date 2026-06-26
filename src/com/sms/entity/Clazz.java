package com.sms.entity;

public class Clazz {
    private Integer id;
    private String classNo;
    private String className;
    private Integer majorId;
    private Integer enrollYear;
    private Integer headTeacherId;

    // Joint fields for displays
    private String majorName;
    private String headTeacherName;

    public Clazz() {}

    public Clazz(Integer id, String classNo, String className, Integer majorId, Integer enrollYear, Integer headTeacherId) {
        this.id = id;
        this.classNo = classNo;
        this.className = className;
        this.majorId = majorId;
        this.enrollYear = enrollYear;
        this.headTeacherId = headTeacherId;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getClassNo() { return classNo; }
    public void setClassNo(String classNo) { this.classNo = classNo; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public Integer getMajorId() { return majorId; }
    public void setMajorId(Integer majorId) { this.majorId = majorId; }

    public Integer getEnrollYear() { return enrollYear; }
    public void setEnrollYear(Integer enrollYear) { this.enrollYear = enrollYear; }

    public Integer getHeadTeacherId() { return headTeacherId; }
    public void setHeadTeacherId(Integer headTeacherId) { this.headTeacherId = headTeacherId; }

    public String getMajorName() { return majorName; }
    public void setMajorName(String majorName) { this.majorName = majorName; }

    public String getHeadTeacherName() { return headTeacherName; }
    public void setHeadTeacherName(String headTeacherName) { this.headTeacherName = headTeacherName; }

    @Override
    public String toString() {
        return "Clazz{" +
                "id=" + id +
                ", classNo='" + classNo + '\'' +
                ", className='" + className + '\'' +
                '}';
    }
}
