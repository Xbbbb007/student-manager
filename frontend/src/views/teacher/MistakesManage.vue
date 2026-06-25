<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getTeacherClassMistakeStats } from "../../api/mistake";
import { Warning, User, Histogram } from "@element-plus/icons-vue";

interface ClassStat {
  class_id: number;
  class_name: string;
  total_mistakes: number;
  top_students: { name: string; mistake_count: number }[];
}

const stats = ref<ClassStat[]>([]);
const loading = ref(true);

async function loadData() {
  loading.value = true;
  try {
    const res: any = await getTeacherClassMistakeStats();
    stats.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取班级错题统计数据失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="mistakes-manage" v-loading="loading">
    <div class="header-action">
      <h2>班级错题分析</h2>
    </div>

    <div v-if="stats.length === 0" class="empty-state">
      <el-empty description="当前暂无班级错题数据" />
    </div>

    <div v-else class="stats-grid">
      <div v-for="c in stats" :key="c.class_id" class="class-card">
        <div class="class-header">
          <span class="class-name">{{ c.class_name }}</span>
          <div class="total-badge">
            <el-icon><Warning /></el-icon>
            <span>总计错题: <strong>{{ c.total_mistakes }}</strong> 道</span>
          </div>
        </div>

        <div class="class-body">
          <div class="section-title">
            <el-icon><Histogram /></el-icon>
            <span>高频错题学生 (Top 5)</span>
          </div>

          <div v-if="c.top_students.length === 0" class="no-students">
            暂无学生错题记录
          </div>

          <div v-else class="students-list">
            <div 
              v-for="(s, idx) in c.top_students" 
              :key="s.name"
              class="student-item"
            >
              <div class="student-left">
                <span :class="['rank-badge', `rank-${idx + 1}`]">{{ idx + 1 }}</span>
                <el-icon class="user-icon"><User /></el-icon>
                <span class="stu-name">{{ s.name }}</span>
              </div>
              <span class="cnt-val">{{ s.mistake_count }} 道错题</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mistakes-manage {
  width: 100%;
}
.header-action {
  margin-bottom: 20px;
}
.header-action h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.class-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all 0.3s;
}
.class-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.class-header {
  padding: 16px 20px;
  background: rgba(8, 31, 92, 0.02);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.class-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}
.total-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-danger);
}
.total-badge strong {
  font-size: 15px;
}

.class-body {
  padding: 20px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-secondary);
  margin-bottom: 14px;
}

.students-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--color-bg-content);
  border-radius: 8px;
  border: 1px solid transparent;
}
.student-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.rank-badge {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: #cbd5e1;
}
.rank-1 {
  background: #f59e0b;
}
.rank-2 {
  background: #94a3b8;
}
.rank-3 {
  background: #b45309;
}
.user-icon {
  color: var(--color-text-light);
}
.stu-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.cnt-val {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.no-students {
  text-align: center;
  padding: 20px 0;
  font-size: 13px;
  color: var(--color-text-light);
}
.empty-state {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
  padding: 60px 0;
}
</style>
