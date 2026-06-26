package com.sms.service;

import com.sms.entity.Clazz;
import com.sms.entity.Department;
import com.sms.entity.Major;
import com.sms.entity.Student;
import com.sms.entity.Teacher;
import java.util.List;

public interface AdminService {
    // Department
    void addDepartment(Department dept);
    void updateDepartment(Department dept);
    void deleteDepartment(Integer id);
    Department getDepartmentById(Integer id);
    List<Department> listAllDepartments();

    // Major
    void addMajor(Major major);
    void updateMajor(Major major);
    void deleteMajor(Integer id);
    Major getMajorById(Integer id);
    List<Major> listAllMajors();
    List<Major> listMajorsByDept(Integer deptId);

    // Clazz
    void addClazz(Clazz clazz);
    void updateClazz(Clazz clazz);
    void deleteClazz(Integer id);
    Clazz getClazzById(Integer id);
    List<Clazz> listAllClazzes();
    List<Clazz> listClazzesByMajor(Integer majorId);

    // Teacher
    Teacher addTeacher(Teacher teacher, String username, String password);
    void updateTeacher(Teacher teacher);
    void deleteTeacher(Integer id);
    Teacher getTeacherById(Integer id);
    Teacher getTeacherByUserId(Integer userId);
    Teacher getTeacherByNo(String teacherNo);
    List<Teacher> listAllTeachers();

    // Student
    Student addStudent(Student student, String username, String password);
    void updateStudent(Student student);
    void deleteStudent(Integer id);
    Student getStudentById(Integer id);
    Student getStudentByUserId(Integer userId);
    Student getStudentByNo(String studentNo);
    List<Student> listAllStudents();
    List<Student> listStudentsByClass(Integer classId);
    List<Student> searchStudents(String queryStr, Integer classId, Integer majorId, int page, int pageSize);
    int countStudents(String queryStr, Integer classId, Integer majorId);
    void changeStudentClass(Integer studentId, Integer targetClassId);

    // CSV Imports / Exports
    int importStudentsFromCSV(String filePath) throws Exception;
    void exportStudentsToCSV(String filePath) throws Exception;
}
