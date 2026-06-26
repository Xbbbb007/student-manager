package com.sms.entity;

import java.sql.Date;

public class Attendance {
    private Integer id;
    private Integer studentId;
    private Integer teachingPlanId;
    private Date attendDate;
    private String status; // 出勤, 迟到, 早退, 旷课, 请假
    private String remark;

    // Joint fields for displays
    private String studentNo;
    private String studentName;
    private String courseName;
    private String className;
    private String semester;

    public Attendance() {}

    public Attendance(Integer id, Integer studentId, Integer teachingPlanId, Date attendDate, String status, String remark) {
        this.id = id;
        this.studentId = studentId;
        this.teachingPlanId = teachingPlanId;
        this.attendDate = attendDate;
        this.status = status;
        this.remark = remark;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getStudentId() { return studentId; }
    public void setStudentId(Integer studentId) { this.studentId = studentId; }

    public Integer getTeachingPlanId() { return teachingPlanId; }
    public void setTeachingPlanId(Integer teachingPlanId) { this.teachingPlanId = teachingPlanId; }

    public Date getAttendDate() { return attendDate; }
    public void setAttendDate(Date attendDate) { this.attendDate = attendDate; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getRemark() { return remark; }
    public void setRemark(String remark) { this.remark = remark; }

    public String getStudentNo() { return studentNo; }
    public void setStudentNo(String studentNo) { this.studentNo = studentNo; }

    public String getStudentName() { return studentName; }
    public void setStudentName(String studentName) { this.studentName = studentName; }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getSemester() { return semester; }
    public void setSemester(String semester) { this.semester = semester; }

    @Override
    public String toString() {
        return "Attendance{" +
                "id=" + id +
                ", studentName='" + studentName + '\'' +
                ", attendDate=" + attendDate +
                ", status='" + status + '\'' +
                '}';
    }
}
