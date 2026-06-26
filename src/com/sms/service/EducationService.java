package com.sms.service;

import com.sms.entity.Attendance;
import com.sms.entity.LeaveRequest;
import com.sms.entity.Notice;
import com.sms.entity.Score;
import java.sql.Date;
import java.util.List;
import java.util.Map;

public interface EducationService {
    // Score Management
    void recordScore(Score score);
    void updateScore(Score score);
    void deleteScore(Integer id);
    Score getScoreById(Integer id);
    List<Score> listScoresByPlan(Integer planId);
    List<Score> listScoresByStudent(Integer studentId, String semester);
    List<Score> listScoresByClassAndCourse(Integer classId, Integer courseId, String semester);
    
    // Statistics & Calculations
    double calculateGPA(Integer studentId, String semester);
    Map<String, Object> calculatePlanScoreStats(Integer planId);
    List<Score> getRankedScores(Integer planId);
    void exportScoresToCSV(Integer planId, String filePath) throws Exception;

    // Attendance Management
    void takeAttendance(Integer planId, Date date, List<Attendance> attendanceList);
    List<Attendance> listAttendanceByStudent(Integer studentId);
    List<Attendance> listAttendanceByStudentAndPlan(Integer studentId, Integer planId);
    List<Attendance> listAttendanceByPlanAndDate(Integer planId, Date date);
    Map<String, Object> calculateAttendanceStats(Integer studentId, Integer planId);

    // Leave Requests
    void applyLeave(LeaveRequest request);
    void approveLeave(Integer requestId, String status, Integer approverUserId, String remark);
    List<LeaveRequest> listLeavesByStudent(Integer studentId);
    List<LeaveRequest> listPendingLeavesByTeacher(Integer teacherUserId);
    List<LeaveRequest> listAllLeaves();

    // Notices
    void publishNotice(Notice notice);
    void recallNotice(Integer noticeId);
    List<Notice> listNoticesForUser(Integer userId);
    List<Notice> listAllNotices();
}
