<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { getScheduleMy } from "../../api/scores";

interface ScheduleItem {
  id: number;
  class_id: number;
  day_of_week: number;
  period: number;
  subject: string;
  subject_name: string;
  teacher_name: string;
}

const days = ["周一", "周二", "周三", "周四", "周五"];
const periods = [
  { label: 1, time: "8:00-8:40" },
  { label: 2, time: "8:50-9:30" },
  { label: 3, time: "10:00-10:40" },
  { label: 4, time: "10:50-11:30" },
  { label: 5, time: "14:00-14:40" },
  { label: 6, time: "14:50-15:30" },
];

const SUBJECT_COLORS: Record<string, { bg: string; text: string }> = {
  chinese: { bg: "#EFF6FF", text: "#1D4ED8" },
  math: { bg: "#ECFDF5", text: "#047857" },
  english: { bg: "#FFFBEB", text: "#B45309" },
  science: { bg: "#F5F3FF", text: "#6D28D9" },
  ethics: { bg: "#FDF2F8", text: "#BE185D" },
  pe: { bg: "#FFF7ED", text: "#C2410C" },
  music: { bg: "#FEF2F2", text: "#B91C1C" },
  art: { bg: "#ECFEFF", text: "#0E7490" },
  it: { bg: "#EEF2FF", text: "#4338CA" },
  "self-study": { bg: "#F9FAFB", text: "#4B5563" },
};

const schedule = ref<ScheduleItem[]>([]);
const loading = ref(true);
const viewMode = ref<"week" | "day">("week");

// 辅助函数获取当前的星期几（1-5）
const getTodayDay = () => {
  const d = new Date().getDay();
  if (d === 0 || d === 6) return 1;
  return d;
};
const selectedDay = ref<number>(getTodayDay());

const grid = computed(() => {
  const map: Record<string, ScheduleItem | null> = {};
  for (const s of schedule.value) {
    map[`${s.day_of_week}-${s.period}`] = s;
  }
  return map;
});

const dayCourses = computed(() => {
  return schedule.value
    .filter((s) => s.day_of_week === selectedDay.value)
    .sort((a, b) => a.period - b.period);
});

function getStyle(sub: string) {
  return SUBJECT_COLORS[sub] || { bg: "#F3F4F6", text: "#6B7280" };
}

function getPeriodTime(periodNum: number) {
  const p = periods.find((x) => x.label === periodNum);
  return p ? p.time : "";
}

onMounted(async () => {
  try {
    const res: any = await getScheduleMy();
    schedule.value = res.data || [];
  } catch (e) {
    console.error("加载课表失败", e);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="schedule-page" v-loading="loading">
    <!-- 顶部排控制条 -->
    <div class="schedule-ctrls">
      <el-radio-group v-model="viewMode" size="default">
        <el-radio-button value="week">周课表</el-radio-button>
        <el-radio-button value="day">日课表</el-radio-button>
      </el-radio-group>

      <!-- 仅在日视图下呈现星期 Tabs -->
      <div v-if="viewMode === 'day'" class="day-tabs">
        <span
          v-for="(dayName, idx) in days"
          :key="idx"
          :class="['day-tab-item', { active: selectedDay === idx + 1 }]"
          @click="selectedDay = idx + 1"
        >
          {{ dayName }}
        </span>
      </div>
    </div>

    <!-- 1. 周课表 (网格视图) -->
    <div v-if="viewMode === 'week'" class="schedule-grid animate-fade">
      <div class="grid-header">
        <div class="th-time"></div>
        <div
          v-for="(d, i) in days"
          :key="i"
          :class="['th-day', { 'today': (i + 1) === getTodayDay() }]"
        >
          {{ d }}
        </div>
      </div>
      <div v-for="p in periods" :key="p.label" class="grid-row">
        <div class="td-time">
          <div class="period-num">{{ p.label }}</div>
          <div class="period-time">{{ p.time }}</div>
        </div>
        <div v-for="d in 5" :key="d" class="td-cell">
          <template v-if="grid[`${d}-${p.label}`]">
            <div class="course-block" :style="{ background: getStyle(grid[`${d}-${p.label}`]?.subject || '').bg, color: getStyle(grid[`${d}-${p.label}`]?.subject || '').text }">
              <div class="course-name">{{ grid[`${d}-${p.label}`]?.subject_name }}</div>
              <div class="course-teacher">{{ grid[`${d}-${p.label}`]?.teacher_name }}</div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 2. 日课表 (垂直时间线 Timeline) -->
    <div v-else class="day-timeline-view animate-fade">
      <div v-if="dayCourses.length === 0" class="no-courses">
        <el-empty description="今天没有安排课程哦" :image-size="80" />
      </div>
      <div v-else class="timeline-container">
        <el-timeline>
          <el-timeline-item
            v-for="c in dayCourses"
            :key="c.id"
            :timestamp="getPeriodTime(c.period)"
            placement="top"
            :color="getStyle(c.subject).text"
          >
            <div class="timeline-card" :style="{ borderLeft: `4px solid ${getStyle(c.subject).text}`, background: getStyle(c.subject).bg }">
              <div class="card-left">
                <span class="period-tag" :style="{ background: getStyle(c.subject).text, color: '#FFFFFF' }">
                  第 {{ c.period }} 节
                </span>
                <span class="subject-title" :style="{ color: getStyle(c.subject).text }">
                  {{ c.subject_name }}
                </span>
              </div>
              <div class="card-right">
                <span class="teacher-info">授课教师：<strong>{{ c.teacher_name }}</strong></span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-page {
  padding: 0;
}

/* ====== 控制条 ====== */
.schedule-ctrls {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.schedule-ctrls :deep(.el-radio-group) {
  background: #F3F4F6;
  padding: 4px;
  border-radius: 12px;
}
.schedule-ctrls :deep(.el-radio-button__inner) {
  border: none !important;
  background: transparent !important;
  border-radius: 10px !important;
  font-weight: 600;
  font-size: 13px;
  padding: 8px 22px;
  box-shadow: none !important;
  color: #6B7280;
  transition: all 0.25s;
}
.schedule-ctrls :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #FFFFFF !important;
  color: #334EAC !important;
  box-shadow: 0 2px 8px rgba(51,78,172,0.12) !important;
}

.day-tabs {
  display: flex;
  background: #F3F4F6;
  padding: 4px;
  border-radius: 12px;
  gap: 2px;
}
.day-tab-item {
  padding: 7px 18px;
  font-size: 13px;
  font-weight: 600;
  color: #6B7280;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.day-tab-item:hover {
  color: #334EAC;
}
.day-tab-item.active {
  background: #FFFFFF;
  color: #334EAC;
  box-shadow: 0 2px 8px rgba(51,78,172,0.12);
}

/* ====== 周视图 ====== */
.schedule-grid {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(8,31,92,0.06);
}
.grid-header {
  display: grid;
  grid-template-columns: 80px repeat(5, 1fr);
  border-bottom: none;
  background: linear-gradient(135deg, #334EAC 0%, #5B74C9 50%, #7B93DB 100%);
  position: relative;
}
.th-time { padding: 14px 8px; }
.th-day {
  padding: 14px 8px;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: rgba(255,255,255,0.8);
  letter-spacing: 0.5px;
  position: relative;
}
.th-day.today {
  color: #FFFFFF;
}
.th-day.today::after {
  content: "今天";
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  font-weight: 700;
  background: rgba(255,255,255,0.25);
  color: #FFFFFF;
  padding: 1px 8px;
  border-radius: 8px;
  letter-spacing: 1px;
}

.grid-row {
  display: grid;
  grid-template-columns: 80px repeat(5, 1fr);
  border-bottom: 1px solid #F3F4F6;
  min-height: 76px;
  transition: background 0.2s;
}
.grid-row:last-child { border-bottom: none; }
.grid-row:hover { background: rgba(51,78,172,0.015); }

.td-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  border-right: 1px solid #F0F0F0;
  background: linear-gradient(180deg, #FAFBFC, #F5F6F8);
}
.period-num {
  font-size: 15px;
  font-weight: 800;
  color: #334EAC;
  background: linear-gradient(135deg, #334EAC, #5B74C9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.period-time {
  font-size: 10px;
  color: #9CA3AF;
  margin-top: 3px;
  font-weight: 500;
}
.td-cell {
  padding: 5px;
  display: flex;
  align-items: stretch;
}

.course-block {
  flex: 1;
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.04);
}
.course-block::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 3px 0 0 3px;
  background: currentColor;
  opacity: 0.4;
}
.course-block:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  border-color: rgba(0,0,0,0.06);
}
.course-name {
  font-size: 14px;
  font-weight: 700;
  line-height: 1.3;
}
.course-teacher {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 3px;
  font-weight: 500;
}

/* ====== Timeline 日视图 ====== */
.day-timeline-view {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  padding: 36px 48px;
  box-shadow: 0 4px 20px rgba(8,31,92,0.06);
}
.timeline-container {
  max-width: 620px;
  margin: 0 auto;
}

/* 自定义 el-timeline 样式 */
.day-timeline-view :deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}
.day-timeline-view :deep(.el-timeline-item__tail) {
  border-left: 2px solid transparent;
  background: linear-gradient(180deg, rgba(51,78,172,0.15), rgba(16,185,129,0.15));
  border-radius: 2px;
  width: 2px;
  left: 0;
}
.day-timeline-view :deep(.el-timeline-item__node) {
  width: 14px;
  height: 14px;
  left: -6px;
  box-shadow: 0 0 0 4px rgba(51,78,172,0.1);
}
.day-timeline-view :deep(.el-timeline-item__timestamp) {
  font-weight: 700;
  font-size: 12px;
  color: #334EAC;
}

.timeline-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 22px;
  border-radius: 12px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgba(0,0,0,0.04);
}
.timeline-card:hover {
  transform: translateX(6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
.card-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.period-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 10px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.subject-title {
  font-size: 16px;
  font-weight: 700;
}
.card-right {
  font-size: 13px;
  color: #6B7280;
}
.teacher-info strong {
  color: #1F2937;
  font-weight: 700;
}
.no-courses {
  padding: 40px 0;
}

/* ====== 动效 ====== */
.animate-fade {
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 课程块交错入场 */
.course-block {
  animation: blockPop 0.35s ease both;
}
@keyframes blockPop {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}
</style>
