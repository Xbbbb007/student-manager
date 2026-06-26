package com.sms.dao;

import com.sms.entity.Notice;
import java.util.List;

public interface NoticeDAO {
    Notice findById(Integer id);
    int insert(Notice notice);
    int update(Notice notice);
    int deleteById(Integer id);
    List<Notice> findByRole(String targetRole);
    List<Notice> findAll();
}
