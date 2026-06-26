package com.sms.entity;

import java.sql.Timestamp;

public class Score {
    private Integer id;
    private Integer teachingPlanId;
    private Integer studentId;
    private Double score;
    private String gradeLevel; // A, B, C, D, F
    private String examType; // 平时, 期中, 期末
    private Timestamp createdAt;
    private Timestamp updatedAt;

    // Joint fields for easier displays
    private String studentNo;
    private String studentName;
    private String className;
    private String courseNo;
    private String courseName;
    private Double courseCredit;
    private String semester;

    public Score() {}

    public Score(Integer id, Integer teachingPlanId, Integer studentId, Double score, String gradeLevel, String examType) {
        this.id = id;
        this.teachingPlanId = teachingPlanId;
        this.studentId = studentId;
        this.score = score;
        this.gradeLevel = gradeLevel;
        this.examType = examType;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getTeachingPlanId() { return teachingPlanId; }
    public void setTeachingPlanId(Integer teachingPlanId) { this.teachingPlanId = teachingPlanId; }

    public Integer getStudentId() { return studentId; }
    public void setStudentId(Integer studentId) { this.studentId = studentId; }

    public Double getScore() { return score; }
    public void setScore(Double score) { this.score = score; }

    public String getGradeLevel() { return gradeLevel; }
    public void setGradeLevel(String gradeLevel) { this.gradeLevel = gradeLevel; }

    public String getExamType() { return examType; }
    public void setExamType(String examType) { this.examType = examType; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    public Timestamp getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Timestamp updatedAt) { this.updatedAt = updatedAt; }

    public String getStudentNo() { return studentNo; }
    public void setStudentNo(String studentNo) { this.studentNo = studentNo; }

    public String getStudentName() { return studentName; }
    public void setStudentName(String studentName) { this.studentName = studentName; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getCourseNo() { return courseNo; }
    public void setCourseNo(String courseNo) { this.courseNo = courseNo; }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }

    public Double getCourseCredit() { return courseCredit; }
    public void setCourseCredit(Double courseCredit) { this.courseCredit = courseCredit; }

    public String getSemester() { return semester; }
    public void setSemester(String semester) { this.semester = semester; }

    @Override
    public String toString() {
        return "Score{" +
                "id=" + id +
                ", studentName='" + studentName + '\'' +
                ", courseName='" + courseName + '\'' +
                ", score=" + score +
                ", examType='" + examType + '\'' +
                '}';
    }
}
