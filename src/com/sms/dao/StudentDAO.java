package com.sms.dao;

import com.sms.entity.Student;
import java.util.List;

public interface StudentDAO {
    Student findById(Integer id);
    Student findByUserId(Integer userId);
    Student findByStudentNo(String studentNo);
    int insert(Student student);
    int update(Student student);
    int deleteById(Integer id);
    List<Student> findAll();
    List<Student> findByClassId(Integer classId);
    List<Student> searchStudents(String queryStr, Integer classId, Integer majorId, int offset, int limit);
    int countStudents(String queryStr, Integer classId, Integer majorId);
}
