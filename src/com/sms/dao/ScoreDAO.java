package com.sms.dao;

import com.sms.entity.Score;
import java.util.List;

public interface ScoreDAO {
    Score findById(Integer id);
    int insert(Score score);
    int update(Score score);
    int deleteById(Integer id);
    List<Score> findByStudentId(Integer studentId, String semester);
    List<Score> findByTeachingPlanId(Integer planId);
    Score findByStudentAndPlanAndExamType(Integer studentId, Integer planId, String examType);
    List<Score> findByClassAndCourse(Integer classId, Integer courseId, String semester);
}
