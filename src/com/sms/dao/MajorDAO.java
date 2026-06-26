package com.sms.dao;

import com.sms.entity.Major;
import java.util.List;

public interface MajorDAO {
    Major findById(Integer id);
    Major findByMajorNo(String majorNo);
    int insert(Major major);
    int update(Major major);
    int deleteById(Integer id);
    List<Major> findAll();
    List<Major> findByDeptId(Integer deptId);
}
