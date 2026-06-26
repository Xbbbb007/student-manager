package com.sms.dao;

import com.sms.entity.User;
import java.util.List;

public interface UserDAO {
    User findById(Integer id);
    User findByUsername(String username);
    int insert(User user);
    int update(User user);
    int deleteById(Integer id);
    List<User> findAll();
}
