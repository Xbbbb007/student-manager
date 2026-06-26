package com.sms.dao;

import com.sms.entity.TeachingPlan;
import java.util.List;

public interface TeachingPlanDAO {
    TeachingPlan findById(Integer id);
    int insert(TeachingPlan plan);
    int update(TeachingPlan plan);
    int deleteById(Integer id);
    List<TeachingPlan> findAll();
    List<TeachingPlan> findBySemester(String semester);
    List<TeachingPlan> findByClassId(Integer classId, String semester);
    List<TeachingPlan> findByTeacherId(Integer teacherId, String semester);
    List<TeachingPlan> findElectives(String semester);
}
