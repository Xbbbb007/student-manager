package com.sms.dao;

import com.sms.entity.LeaveRequest;
import java.util.List;

public interface LeaveRequestDAO {
    LeaveRequest findById(Integer id);
    int insert(LeaveRequest request);
    int update(LeaveRequest request);
    int deleteById(Integer id);
    List<LeaveRequest> findByStudentId(Integer studentId);
    List<LeaveRequest> findPendingByTeacherId(Integer teacherId);
    List<LeaveRequest> findAll();
}
