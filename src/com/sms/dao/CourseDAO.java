package com.sms.dao;

import com.sms.entity.Course;
import java.util.List;

public interface CourseDAO {
    Course findById(Integer id);
    Course findByCourseNo(String courseNo);
    int insert(Course course);
    int update(Course course);
    int deleteById(Integer id);
    List<Course> findAll();
}
