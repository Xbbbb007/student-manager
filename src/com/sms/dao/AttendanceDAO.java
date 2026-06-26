package com.sms.dao;

import com.sms.entity.Attendance;
import java.sql.Date;
import java.util.List;

public interface AttendanceDAO {
    Attendance findById(Integer id);
    int insert(Attendance attendance);
    int update(Attendance attendance);
    int deleteById(Integer id);
    List<Attendance> findByStudentId(Integer studentId);
    List<Attendance> findByStudentAndCourse(Integer studentId, Integer planId);
    List<Attendance> findByPlanAndDate(Integer planId, Date date);
    Attendance findByStudentAndPlanAndDate(Integer studentId, Integer planId, Date date);
}
