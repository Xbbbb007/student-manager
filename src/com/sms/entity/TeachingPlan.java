package com.sms.entity;

public class TeachingPlan {
    private Integer id;
    private Integer courseId;
    private Integer teacherId;
    private Integer classId;
    private String semester;
    private Integer maxStudents;
    private Integer currentStudents;

    // Joint fields for easier displays
    private String courseNo;
    private String courseName;
    private String courseType;
    private Double courseCredit;
    private String teacherNo;
    private String teacherName;
    private String classNo;
    private String className;

    public TeachingPlan() {}

    public TeachingPlan(Integer id, Integer courseId, Integer teacherId, Integer classId, String semester, Integer maxStudents, Integer currentStudents) {
        this.id = id;
        this.courseId = courseId;
        this.teacherId = teacherId;
        this.classId = classId;
        this.semester = semester;
        this.maxStudents = maxStudents;
        this.currentStudents = currentStudents;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getCourseId() { return courseId; }
    public void setCourseId(Integer courseId) { this.courseId = courseId; }

    public Integer getTeacherId() { return teacherId; }
    public void setTeacherId(Integer teacherId) { this.teacherId = teacherId; }

    public Integer getClassId() { return classId; }
    public void setClassId(Integer classId) { this.classId = classId; }

    public String getSemester() { return semester; }
    public void setSemester(String semester) { this.semester = semester; }

    public Integer getMaxStudents() { return maxStudents; }
    public void setMaxStudents(Integer maxStudents) { this.maxStudents = maxStudents; }

    public Integer getCurrentStudents() { return currentStudents; }
    public void setCurrentStudents(Integer currentStudents) { this.currentStudents = currentStudents; }

    public String getCourseNo() { return courseNo; }
    public void setCourseNo(String courseNo) { this.courseNo = courseNo; }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }

    public String getCourseType() { return courseType; }
    public void setCourseType(String courseType) { this.courseType = courseType; }

    public Double getCourseCredit() { return courseCredit; }
    public void setCourseCredit(Double courseCredit) { this.courseCredit = courseCredit; }

    public String getTeacherNo() { return teacherNo; }
    public void setTeacherNo(String teacherNo) { this.teacherNo = teacherNo; }

    public String getTeacherName() { return teacherName; }
    public void setTeacherName(String teacherName) { this.teacherName = teacherName; }

    public String getClassNo() { return classNo; }
    public void setClassNo(String classNo) { this.classNo = classNo; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    @Override
    public String toString() {
        return "TeachingPlan{" +
                "id=" + id +
                ", courseName='" + courseName + '\'' +
                ", teacherName='" + teacherName + '\'' +
                ", className='" + className + '\'' +
                ", semester='" + semester + '\'' +
                '}';
    }
}
