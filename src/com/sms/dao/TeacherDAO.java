package com.sms.dao;

import com.sms.entity.Teacher;
import java.util.List;

public interface TeacherDAO {
    Teacher findById(Integer id);
    Teacher findByUserId(Integer userId);
    Teacher findByTeacherNo(String teacherNo);
    int insert(Teacher teacher);
    int update(Teacher teacher);
    int deleteById(Integer id);
    List<Teacher> findAll();
    List<Teacher> findByDeptId(Integer deptId);
}
