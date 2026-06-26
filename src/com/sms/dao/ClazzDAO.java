package com.sms.dao;

import com.sms.entity.Clazz;
import java.util.List;

public interface ClazzDAO {
    Clazz findById(Integer id);
    Clazz findByClassNo(String classNo);
    int insert(Clazz clazz);
    int update(Clazz clazz);
    int deleteById(Integer id);
    List<Clazz> findAll();
    List<Clazz> findByMajorId(Integer majorId);
}
