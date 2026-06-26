<script setup lang="ts">
import { ref } from "vue";
import HomeworkManage from "./HomeworkManage.vue";
import ExamScheduleManage from "./ExamScheduleManage.vue";
import MistakesManage from "./MistakesManage.vue";
import AttendanceManage from "./AttendanceManage.vue";
import ExamPaperManage from "./ExamPaperManage.vue";
import ResourceLibrary from "./ResourceLibrary.vue";
import { DocumentCopy, Calendar, Notebook, Checked, FolderOpened, Files } from "@element-plus/icons-vue";

const activeSubTab = ref("homework");
</script>

<template>
  <div class="teach-page">
    <div class="teach-sidebar-layout">
      <!-- 内部子菜单/侧边栏 -->
      <aside class="teach-aside">
        <div class="aside-title">教学事务</div>
        <ul class="aside-menu">
          <li 
            :class="['menu-item', { active: activeSubTab === 'homework' }]"
            @click="activeSubTab = 'homework'"
          >
            <el-icon><DocumentCopy /></el-icon>
            <span>作业管理</span>
          </li>
          <li 
            :class="['menu-item', { active: activeSubTab === 'exams' }]"
            @click="activeSubTab = 'exams'"
          >
            <el-icon><Calendar /></el-icon>
            <span>考试安排</span>
          </li>
          <li 
            :class="['menu-item', { active: activeSubTab === 'mistakes' }]"
            @click="activeSubTab = 'mistakes'"
          >
            <el-icon><Notebook /></el-icon>
            <span>错题统计</span>
          </li>
          <li 
            :class="['menu-item', { active: activeSubTab === 'attendance' }]"
            @click="activeSubTab = 'attendance'"
          >
            <el-icon><Checked /></el-icon>
            <span>考勤管理</span>
          </li>
          <li 
            :class="['menu-item', { active: activeSubTab === 'papers' }]"
            @click="activeSubTab = 'papers'"
          >
            <el-icon><Files /></el-icon>
            <span>出卷组卷</span>
          </li>
          <li 
            :class="['menu-item', { active: activeSubTab === 'resources' }]"
            @click="activeSubTab = 'resources'"
          >
            <el-icon><FolderOpened /></el-icon>
            <span>资源库</span>
          </li>
        </ul>
      </aside>

      <!-- 主要内容区 -->
      <main class="teach-main-body">
        <div class="teach-card">
          <HomeworkManage v-if="activeSubTab === 'homework'" />
          <ExamScheduleManage v-else-if="activeSubTab === 'exams'" />
          <MistakesManage v-else-if="activeSubTab === 'mistakes'" />
          <AttendanceManage v-else-if="activeSubTab === 'attendance'" />
          <ExamPaperManage v-else-if="activeSubTab === 'papers'" />
          <ResourceLibrary v-else-if="activeSubTab === 'resources'" />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.teach-page {
  height: 100%;
}
.teach-sidebar-layout {
  display: flex;
  min-height: calc(100vh - 100px);
  gap: 24px;
}
.teach-aside {
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

.teach-main-body {
  flex: 1;
  min-width: 0;
}
.teach-card {
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
