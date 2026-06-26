package com.sms.entity;

import java.sql.Timestamp;

public class Notice {
    private Integer id;
    private String title;
    private String content;
    private Integer publisherId;
    private String targetRole; // ALL, TEACHER, STUDENT
    private Integer isTop; // 1: top, 0: normal
    private Integer status; // 1: normal, 0: recalled
    private Timestamp createdAt;

    // Joint field
    private String publisherName;

    public Notice() {}

    public Notice(Integer id, String title, String content, Integer publisherId, String targetRole, Integer isTop, Integer status) {
        this.id = id;
        this.title = title;
        this.content = content;
        this.publisherId = publisherId;
        this.targetRole = targetRole;
        this.isTop = isTop;
        this.status = status;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public Integer getPublisherId() { return publisherId; }
    public void setPublisherId(Integer publisherId) { this.publisherId = publisherId; }

    public String getTargetRole() { return targetRole; }
    public void setTargetRole(String targetRole) { this.targetRole = targetRole; }

    public Integer getIsTop() { return isTop; }
    public void setIsTop(Integer isTop) { this.isTop = isTop; }

    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    public String getPublisherName() { return publisherName; }
    public void setPublisherName(String publisherName) { this.publisherName = publisherName; }

    @Override
    public String toString() {
        return "Notice{" +
                "id=" + id +
                ", title='" + title + '\'' +
                ", publisherName='" + publisherName + '\'' +
                ", isTop=" + isTop +
                '}';
    }
}
