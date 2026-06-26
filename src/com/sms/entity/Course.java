package com.sms.entity;

public class Course {
    private Integer id;
    private String courseNo;
    private String courseName;
    private Double credit;
    private Integer hours;
    private String type; // 必修, 选修, 公选

    public Course() {}

    public Course(Integer id, String courseNo, String courseName, Double credit, Integer hours, String type) {
        this.id = id;
        this.courseNo = courseNo;
        this.courseName = courseName;
        this.credit = credit;
        this.hours = hours;
        this.type = type;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getCourseNo() { return courseNo; }
    public void setCourseNo(String courseNo) { this.courseNo = courseNo; }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }

    public Double getCredit() { return credit; }
    public void setCredit(Double credit) { this.credit = credit; }

    public Integer getHours() { return hours; }
    public void setHours(Integer hours) { this.hours = hours; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    @Override
    public String toString() {
        return "Course{" +
                "id=" + id +
                ", courseNo='" + courseNo + '\'' +
                ", courseName='" + courseName + '\'' +
                ", credit=" + credit +
                ", type='" + type + '\'' +
                '}';
    }
}
