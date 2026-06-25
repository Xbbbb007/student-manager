<script setup lang="ts">
import { ref } from "vue";
import HomeworkOverview from "./HomeworkOverview.vue";
import AdminExamSchedule from "./AdminExamSchedule.vue";
import AdminMistakes from "./AdminMistakes.vue";
import AdminAttendance from "./AdminAttendance.vue";
import { Monitor, Calendar, Coordinate, Notebook, Checked } from "@element-plus/icons-vue";

const activeTab = ref("homework");
</script>

<template>
  <div class="edu-page">
    <div class="edu-sidebar-layout">
      <!-- 内部子菜单/侧边栏 -->
      <aside class="edu-aside">
        <div class="aside-title">教务管理系统</div>
        <ul class="aside-menu">
          <li 
            :class="['menu-item', { active: activeTab === 'homework' }]"
            @click="activeTab = 'homework'"
          >
            <el-icon><Monitor /></el-icon>
            <span>作业监控</span>
          </li>
          <li 
            :class="['menu-item', { active: activeTab === 'schedule' }]"
            @click="activeTab = 'schedule'"
          >
            <el-icon><Calendar /></el-icon>
            <span>课表排课</span>
          </li>
          <li 
            :class="['menu-item', { active: activeTab === 'exams' }]"
            @click="activeTab = 'exams'"
          >
            <el-icon><Coordinate /></el-icon>
            <span>考试管理</span>
          </li>
          <li 
            :class="['menu-item', { active: activeTab === 'mistakes' }]"
            @click="activeTab = 'mistakes'"
          >
            <el-icon><Notebook /></el-icon>
            <span>错题分析</span>
          </li>
          <li 
            :class="['menu-item', { active: activeTab === 'attendance' }]"
            @click="activeTab = 'attendance'"
          >
            <el-icon><Checked /></el-icon>
            <span>考勤统计</span>
          </li>
        </ul>
      </aside>

      <!-- 主要内容区 -->
      <main class="edu-main-body">
        <div class="edu-card">
          <HomeworkOverview v-if="activeTab === 'homework'" />
          <AdminExamSchedule v-else-if="activeTab === 'exams'" />
          <AdminMistakes v-else-if="activeTab === 'mistakes'" />
          <AdminAttendance v-else-if="activeTab === 'attendance'" />
          
          <div v-else class="placeholder-view">
            <el-empty description="智能课表排课系统开发中..." />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.edu-page {
  height: 100%;
}
.edu-sidebar-layout {
  display: flex;
  min-height: calc(100vh - 100px);
  gap: 24px;
}
.edu-aside {
  width: 220px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 20px 12px;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  height: fit-content;
}
.aside-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  padding-left: 12px;
}
.aside-menu {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.25s;
}
.menu-item:hover {
  color: var(--color-primary);
  background: var(--color-border-light);
}
.menu-item.active {
  background: var(--color-primary);
  color: #ffffff;
}

.edu-main-body {
  flex: 1;
  min-width: 0;
}
.edu-card {
  background: var(--color-bg-content);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 28px;
  box-shadow: var(--shadow-sm);
  min-height: 480px;
}

.placeholder-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 380px;
}
</style>
