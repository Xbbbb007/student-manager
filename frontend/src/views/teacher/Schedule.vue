<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { getScheduleClass, getScheduleTeacher, batchUpdateSchedule } from "../../api/scores";
import { useUserStore } from "../../stores/user";
import { ElMessage } from "element-plus";

const userStore = useUserStore();

interface ScheduleItem {
  id: number;
  class_id: number;
  day_of_week: number;
  period: number;
  subject: string;
  subject_name: string;
  teacher_name: string;
}

interface ClassItem {
  id: number;
  name: string;
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

const SUBJECT_OPTIONS = [
  { value: "chinese", label: "语文" },
  { value: "math", label: "数学" },
  { value: "english", label: "英语" },
  { value: "science", label: "科学" },
  { value: "ethics", label: "道德与法治" },
  { value: "pe", label: "体育" },
  { value: "music", label: "音乐" },
  { value: "art", label: "美术" },
  { value: "it", label: "信息科技" },
  { value: "self-study", label: "自习" },
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

const selectedClassId = ref<number | null>(null);
const classList = ref<ClassItem[]>([]);
const schedule = ref<ScheduleItem[]>([]);
const loading = ref(false);
const editing = ref(false);
const editData = ref<Record<string, string>>({});

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

async function loadClasses() {
  try {
    const res: any = await getScheduleTeacher(userStore.userInfo?.id || 0);
    const classes: Record<number, string> = {};
    for (const item of (res.data || [])) {
      if (item.class_id && !classes[item.class_id]) {
        classes[item.class_id] = item.class_name;
      }
    }
    classList.value = Object.entries(classes).map(([id, name]) => ({ id: Number(id), name }));
    if (classList.value.length > 0 && !selectedClassId.value) {
      selectedClassId.value = classList.value[0].id;
    }
  } catch (e) {
    console.error("加载班级列表失败", e);
  }
}

async function loadSchedule() {
  if (!selectedClassId.value) { schedule.value = []; return; }
  loading.value = true;
  try {
    const res: any = await getScheduleClass(selectedClassId.value);
    schedule.value = res.data || [];
  } catch (e) {
    console.error("加载课表失败", e);
  } finally {
    loading.value = false;
  }
}

watch(selectedClassId, loadSchedule);

function startEdit() {
  editing.value = true;
  editData.value = {};
  for (const s of schedule.value) {
    editData.value[`${s.day_of_week}-${s.period}`] = s.subject;
  }
}

function getEditValue(day: number, period: number): string {
  return editData.value[`${day}-${period}`] || "";
}

function setEditValue(day: number, period: number, val: string) {
  editData.value[`${day}-${period}`] = val;
}

async function saveEdit() {
  if (!selectedClassId.value) return;
  const items: Array<{ day_of_week: number; period: number; subject: string }> = [];
  for (const day of [1, 2, 3, 4, 5]) {
    for (let p = 1; p <= 6; p++) {
      const sub = editData.value[`${day}-${p}`];
      if (sub) {
        items.push({ day_of_week: day, period: p, subject: sub });
      }
    }
  }
  try {
    await batchUpdateSchedule(selectedClassId.value, items);
    ElMessage.success("课表保存成功");
    editing.value = false;
    await loadSchedule();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  }
}

function cancelEdit() {
  editing.value = false;
  editData.value = {};
}

onMounted(() => {
  loadClasses();
});
</script>

<template>
  <div class="schedule-page">
    <div class="page-header">
      <h2>课表管理</h2>
      <div class="header-actions">
        <el-select v-model="selectedClassId" placeholder="选择班级" style="width: 180px">
          <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button v-if="!editing" type="primary" size="small" @click="startEdit">编辑课表</el-button>
        <template v-if="editing">
          <el-button type="success" size="small" @click="saveEdit">保存</el-button>
          <el-button size="small" @click="cancelEdit">取消</el-button>
        </template>
      </div>
    </div>

    <div v-loading="loading" class="schedule-grid">
      <div class="grid-header">
        <div class="th-time"></div>
        <div v-for="(d, i) in days" :key="i" class="th-day">{{ d }}</div>
      </div>
      <div v-for="p in periods" :key="p.label" class="grid-row">
        <div class="td-time">
          <div class="period-num">{{ p.label }}</div>
          <div class="period-time">{{ p.time }}</div>
        </div>
        <div v-for="day in [1,2,3,4,5]" :key="day" class="td-cell">
          <template v-if="editing">
            <el-select
              :model-value="getEditValue(day, p.label)"
              @update:model-value="(v: string) => setEditValue(day, p.label, v)"
              size="small"
              placeholder="选择科目"
              style="width: 100%"
            >
              <el-option v-for="s in SUBJECT_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
          </template>
          <template v-else>
            <div v-if="grid[`${day}-${p.label}`]" class="course-block" :style="{ background: getStyle(grid[`${day}-${p.label}`].subject).bg, color: getStyle(grid[`${day}-${p.label}`].subject).text }">
              <div class="course-name">{{ grid[`${day}-${p.label}`].subject_name }}</div>
              <div class="course-teacher">{{ grid[`${day}-${p.label}`].teacher_name }}</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-page { padding: 0; }
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 { font-size: 20px; font-weight: 700; color: #1F2937; margin: 0; }
.header-actions { display: flex; gap: 8px; align-items: center; }
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
}
.course-name { font-size: 14px; font-weight: 700; line-height: 1.2; }
.course-teacher { font-size: 11px; opacity: 0.7; margin-top: 2px; }
</style>
