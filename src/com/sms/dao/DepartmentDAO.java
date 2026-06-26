package com.sms.dao;

import com.sms.entity.Department;
import java.util.List;

public interface DepartmentDAO {
    Department findById(Integer id);
    Department findByDeptNo(String deptNo);
    int insert(Department dept);
    int update(Department dept);
    int deleteById(Integer id);
    List<Department> findAll();
}
