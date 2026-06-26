<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getAdminAttendanceStats } from "../../api/attendance";
import { Warning, UserFilled, Histogram } from "@element-plus/icons-vue";

interface ClassStat {
  class_id: number;
  class_name: string;
  total: number;
  present: number;
  tardy: number;
  absent: number;
  leave: number;
  attendance_rate: number;
}

interface WarningRecord {
  student_name: string;
  class_name: string;
  absent_count: number;
}

const classesStats = ref<ClassStat[]>([]);
const warnings = ref<WarningRecord[]>([]);
const loading = ref(true);

async function loadData() {
  loading.value = true;
  try {
    const res: any = await getAdminAttendanceStats();
    classesStats.value = res.data?.classes || [];
    warnings.value = res.data?.warnings || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取全校考勤统计失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="admin-attendance-page" v-loading="loading">
    <div class="header-title">
      <h2>全校考勤数据大盘</h2>
    </div>

    <!-- 异常缺勤预警标红 -->
    <div class="warning-section" v-if="warnings.length > 0">
      <div class="warning-header">
        <el-icon class="warn-icon"><Warning /></el-icon>
        <h3>异常缺勤学生预警 (缺勤频次 TOP 10)</h3>
      </div>
      <div class="warning-grid">
        <div v-for="w in warnings" :key="w.student_name" class="warn-card">
          <div class="w-avatar"><UserFilled /></div>
          <div class="w-info">
            <span class="w-name">{{ w.student_name }}</span>
            <span class="w-class">{{ w.class_name }}</span>
          </div>
          <span class="w-cnt">{{ w.absent_count }} 次缺勤</span>
        </div>
      </div>
    </div>

    <!-- 班级出勤率排名 -->
    <div class="class-stats-section">
      <div class="section-title">
        <el-icon><Histogram /></el-icon>
        <h3>各班级考勤出勤率统计</h3>
      </div>

      <el-empty description="暂无班级考勤统计数据" v-if="classesStats.length === 0" />
      <div class="class-grid" v-else>
        <div v-for="c in classesStats" :key="c.class_id" class="cstat-card">
          <div class="c-header">
            <span class="c-name">{{ c.class_name }}</span>
            <span :class="['c-rate', { 'text-danger': c.attendance_rate < 90 }]">{{ c.attendance_rate }}% 出勤率</span>
          </div>
          <div class="c-body">
            <el-progress 
              :percentage="c.attendance_rate" 
              :status="c.attendance_rate >= 95 ? 'success' : (c.attendance_rate >= 90 ? 'warning' : 'exception')"
              style="margin-bottom: 12px"
            />
            <div class="detail-row">
              <span class="d-item">出勤: <strong>{{ c.present }}</strong></span>
              <span class="d-item">迟到: <strong>{{ c.tardy }}</strong></span>
              <span class="d-item text-danger">缺勤: <strong>{{ c.absent }}</strong></span>
              <span class="d-item">请假: <strong>{{ c.leave }}</strong></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-attendance-page {
  width: 100%;
}
.header-title {
  margin-bottom: 20px;
}
.header-title h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}

/* Warnings */
.warning-section {
  background: rgba(239, 68, 68, 0.03);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}
.warning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}
.warn-icon {
  font-size: 20px;
  color: var(--color-danger);
}
.warning-header h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-danger);
  margin: 0;
}
.warning-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.warn-card {
  background: var(--color-bg-card);
  border: 1px solid rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--shadow-sm);
}
.w-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}
.w-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.w-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}
.w-class {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.w-cnt {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-danger);
}

/* Class stats */
.class-stats-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  color: var(--color-primary);
}
.section-title h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}
.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.cstat-card {
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  background: rgba(8, 31, 92, 0.01);
  padding: 14px;
}
.c-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.c-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}
.c-rate {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-success);
}
.c-rate.text-danger {
  color: var(--color-danger);
}
.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-secondary);
}
.detail-row strong {
  color: var(--color-text);
}
</style>
