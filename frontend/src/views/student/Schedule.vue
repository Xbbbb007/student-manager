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
  chinese: { bg: "#2C2D35", text: "#FFFFFF" },
  math: { bg: "#D1FAE5", text: "#065F46" },
  english: { bg: "#FEF3C7", text: "#92400E" },
  science: { bg: "#EDE9FE", text: "#5B21B6" },
  ethics: { bg: "#FCE7F3", text: "#9D174D" },
  pe: { bg: "#FFEDD5", text: "#9A3412" },
  music: { bg: "#FEE2E2", text: "#991B1B" },
  art: { bg: "#CFFAFE", text: "#155E75" },
  it: { bg: "#E0E7FF", text: "#3730A3" },
  "self-study": { bg: "#F3F4F6", text: "#6B7280" },
};

const schedule = ref<ScheduleItem[]>([]);
const loading = ref(true);

const grid = computed(() => {
  const map: Record<string, ScheduleItem | null> = {};
  for (const s of schedule.value) {
    map[`${s.day_of_week}-${s.period}`] = s;
  }
  return map;
});

function getStyle(sub: string) {
  return SUBJECT_COLORS[sub] || { bg: "#F3F4F6", text: "#6B7280" };
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
    <div class="schedule-grid">
      <div class="grid-header">
        <div class="th-time"></div>
        <div v-for="(d, i) in days" :key="i" class="th-day" :class="{ 'today': i === 2 }">{{ d }}</div>
      </div>
      <div v-for="p in periods" :key="p.label" class="grid-row">
        <div class="td-time">
          <div class="period-num">{{ p.label }}</div>
          <div class="period-time">{{ p.time }}</div>
        </div>
        <div v-for="d in 5" :key="d" class="td-cell">
          <template v-if="grid[`${d}-${p.label}`]">
            <div class="course-block" :style="{ background: getStyle(grid[`${d}-${p.label}`].subject).bg, color: getStyle(grid[`${d}-${p.label}`].subject).text }">
              <div class="course-name">{{ grid[`${d}-${p.label}`].subject_name }}</div>
              <div class="course-teacher">{{ grid[`${d}-${p.label}`].teacher_name }}</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-page { padding: 0; }
.schedule-grid {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  overflow: hidden;
}
.grid-header {
  display: grid;
  grid-template-columns: 80px repeat(5, 1fr);
  border-bottom: 2px solid #E5E7EB;
  background: #F9F9F9;
}
.th-time { padding: 12px 8px; }
.th-day {
  padding: 12px 8px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: #6B7280;
}
.th-day.today {
  color: #334EAC;
  font-weight: 700;
  position: relative;
}
.th-day.today::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: #334EAC;
  border-radius: 3px;
}
.grid-row {
  display: grid;
  grid-template-columns: 80px repeat(5, 1fr);
  border-bottom: 1px solid #F3F4F6;
  min-height: 72px;
}
.grid-row:last-child { border-bottom: none; }
.td-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  border-right: 1px solid #F3F4F6;
  background: #FAFBFC;
}
.period-num { font-size: 14px; font-weight: 700; color: #1F2937; }
.period-time { font-size: 10px; color: #9CA3AF; margin-top: 2px; }
.td-cell { padding: 4px; display: flex; align-items: stretch; }
.course-block {
  flex: 1;
  border-radius: 4px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.course-block:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.course-name { font-size: 14px; font-weight: 700; line-height: 1.2; }
.course-teacher { font-size: 11px; opacity: 0.7; margin-top: 2px; }
</style>
