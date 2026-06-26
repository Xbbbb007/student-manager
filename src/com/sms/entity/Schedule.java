package com.sms.entity;

public class Schedule {
    private Integer id;
    private Integer teachingPlanId;
    private Integer dayOfWeek; // 1-7 (Mon-Sun)
    private Integer sectionStart; // class period start
    private Integer sectionEnd; // class period end
    private String classroom;
    private String campus;

    // Joint fields for easier displays
    private String courseName;
    private String teacherName;
    private String className;
    private String semester;

    public Schedule() {}

    public Schedule(Integer id, Integer teachingPlanId, Integer dayOfWeek, Integer sectionStart, Integer sectionEnd, String classroom, String campus) {
        this.id = id;
        this.teachingPlanId = teachingPlanId;
        this.dayOfWeek = dayOfWeek;
        this.sectionStart = sectionStart;
        this.sectionEnd = sectionEnd;
        this.classroom = classroom;
        this.campus = campus;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getTeachingPlanId() { return teachingPlanId; }
    public void setTeachingPlanId(Integer teachingPlanId) { this.teachingPlanId = teachingPlanId; }

    public Integer getDayOfWeek() { return dayOfWeek; }
    public void setDayOfWeek(Integer dayOfWeek) { this.dayOfWeek = dayOfWeek; }

    public Integer getSectionStart() { return sectionStart; }
    public void setSectionStart(Integer sectionStart) { this.sectionStart = sectionStart; }

    public Integer getSectionEnd() { return sectionEnd; }
    public void setSectionEnd(Integer sectionEnd) { this.sectionEnd = sectionEnd; }

    public String getClassroom() { return classroom; }
    public void setClassroom(String classroom) { this.classroom = classroom; }

    public String getCampus() { return campus; }
    public void setCampus(String campus) { this.campus = campus; }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }

    public String getTeacherName() { return teacherName; }
    public void setTeacherName(String teacherName) { this.teacherName = teacherName; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getSemester() { return semester; }
    public void setSemester(String semester) { this.semester = semester; }

    @Override
    public String toString() {
        return "Schedule{" +
                "id=" + id +
                ", courseName='" + courseName + '\'' +
                ", dayOfWeek=" + dayOfWeek +
                ", sections=" + sectionStart + "-" + sectionEnd +
                ", classroom='" + classroom + '\'' +
                '}';
    }
}
