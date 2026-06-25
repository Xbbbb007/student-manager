<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { getScheduleClass, getScheduleTeacher, batchUpdateSchedule } from "../../api/scores";
import { useUserStore } from "../../stores/user";
import { ElMessage } from "element-plus";

const userStore = useUserStore();

interface ScheduleItem {
  id: number;
  class_id: number;
  class_name?: string;
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

const viewMode = ref<"class" | "my_day">("class");
const selectedClassId = ref<number | null>(null);
const classList = ref<ClassItem[]>([]);
const schedule = ref<ScheduleItem[]>([]);
const mySchedule = ref<ScheduleItem[]>([]); // 老师个人的跨班总课表
const loading = ref(false);
const editing = ref(false);
const editData = ref<Record<string, string>>({});

// 辅助时间获取星期天数（1-5）
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

// 老师今日跨班上课安排
const myDayCourses = computed(() => {
  return mySchedule.value
    .filter((s) => s.day_of_week === selectedDay.value)
    .sort((a, b) => a.period - b.period);
});

// 检查该课是否为自己上课
function isMyCourse(item?: ScheduleItem | null): boolean {
  if (!item) return false;
  return item.teacher_name === userStore.userInfo?.name;
}

function getStyle(sub: string) {
  return SUBJECT_COLORS[sub] || { bg: "#F3F4F6", text: "#6B7280" };
}

function getPeriodTime(periodNum: number) {
  const p = periods.find((x) => x.label === periodNum);
  return p ? p.time : "";
}

async function loadClasses() {
  try {
    const res: any = await getScheduleTeacher(userStore.userInfo?.id || 0);
    mySchedule.value = res.data || [];
    const classes: Record<number, string> = {};
    for (const item of mySchedule.value) {
      if (item.class_id && !classes[item.class_id]) {
        classes[item.class_id] = item.class_name || "";
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
    // 保持总课表同步
    const res: any = await getScheduleTeacher(userStore.userInfo?.id || 0);
    mySchedule.value = res.data || [];
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
      <div class="header-left">
        <h2>课表管理</h2>
        <!-- 视角切换 -->
        <el-radio-group v-model="viewMode" size="default" style="margin-left: 20px">
          <el-radio-button value="class">班级课表</el-radio-button>
          <el-radio-button value="my_day">我今日的课表</el-radio-button>
        </el-radio-group>
      </div>

      <div class="header-actions">
        <!-- 仅在班级课表视图下显示班级切换及编辑 -->
        <template v-if="viewMode === 'class'">
          <el-select v-model="selectedClassId" placeholder="选择班级" style="width: 180px">
            <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-button v-if="!editing" type="primary" size="small" @click="startEdit">编辑课表</el-button>
          <template v-if="editing">
            <el-button type="success" size="small" @click="saveEdit">保存</el-button>
            <el-button size="small" @click="cancelEdit">取消</el-button>
          </template>
        </template>
        
        <!-- 仅在日视图下呈现星期 Tabs -->
        <div v-else class="day-tabs">
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
    </div>

    <!-- 1. 班级全课表 (网格视图) -->
    <div v-if="viewMode === 'class'" v-loading="loading" class="schedule-grid animate-fade">
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
            <div v-if="grid[`${day}-${p.label}`]" style="flex:1; display:flex;">
              <!-- 自己的课：彩色强调风格 -->
              <div 
                v-if="isMyCourse(grid[`${day}-${p.label}`])" 
                class="course-block my-course" 
                :style="{ background: getStyle(grid[`${day}-${p.label}`].subject).bg, color: getStyle(grid[`${day}-${p.label}`].subject).text, border: `1.5px solid ${getStyle(grid[`${day}-${p.label}`].subject).text}` }"
              >
                <div class="course-name">{{ grid[`${day}-${p.label}`].subject_name }}</div>
                <div class="course-teacher">我 ({{ grid[`${day}-${p.label}`].teacher_name }})</div>
              </div>
              
              <!-- 他人的课：极度置灰淡化 -->
              <div 
                v-else 
                class="course-block other-course"
              >
                <div class="course-name">{{ grid[`${day}-${p.label}`].subject_name }}</div>
                <div class="course-teacher">{{ grid[`${day}-${p.label}`].teacher_name }}</div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 2. 我今日上课时间线 (垂直时间线) -->
    <div v-else class="my-timeline-view animate-fade">
      <div v-if="myDayCourses.length === 0" class="no-courses">
        <el-empty description="今天您不需要上课，好好放松一下吧" :image-size="80" />
      </div>
      <div v-else class="timeline-container">
        <el-timeline>
          <el-timeline-item
            v-for="c in myDayCourses"
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
                <span class="class-tag-name">
                  {{ c.class_name }}
                </span>
              </div>
              <div class="card-right" :style="{ color: getStyle(c.subject).text }">
                <span class="subject-title-name"><strong>{{ c.subject_name }}</strong></span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
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
  flex-wrap: wrap;
  gap: 12px;
}
.header-left {
  display: flex;
  align-items: center;
}
.page-header h2 { font-size: 20px; font-weight: 700; color: #1F2937; margin: 0; }
.header-actions { display: flex; gap: 12px; align-items: center; }

.day-tabs {
  display: flex;
  background: #F3F4F6;
  padding: 4px;
  border-radius: 6px;
}
.day-tab-item {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #4B5563;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}
.day-tab-item:hover {
  color: #1F2937;
}
.day-tab-item.active {
  background: #FFFFFF;
  color: #334EAC;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* 网格样式 */
.schedule-grid {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
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

/* 课程卡片 */
.course-block {
  flex: 1;
  border-radius: 4px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 自己的课：彩色强调 */
.course-block.my-course {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  font-weight: 700;
  transform: scale(1.02);
  z-index: 2;
  cursor: pointer;
}
.course-block.my-course .course-name {
  font-size: 14px;
}
.course-block.my-course .course-teacher {
  font-size: 10px;
  font-weight: 700;
  opacity: 0.95;
}

/* 别人的课：极浅底灰、虚线边、灰色字 */
.course-block.other-course {
  background: #F9FAFB !important;
  color: #9CA3AF !important;
  border: 1px dashed #E5E7EB;
  opacity: 0.55;
  flex: 1;
}
.course-block.other-course .course-name {
  font-size: 12px;
  font-weight: 500;
}
.course-block.other-course .course-teacher {
  font-size: 10px;
  opacity: 0.7;
}

/* Timeline 视图 */
.my-timeline-view {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 30px 40px;
  box-shadow: var(--shadow-sm);
}
.timeline-container {
  max-width: 600px;
  margin: 0 auto;
}
.timeline-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.timeline-card:hover {
  transform: translateX(2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
}
.card-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.period-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
  letter-spacing: 0.5px;
}
.class-tag-name {
  font-size: 15px;
  font-weight: 700;
  color: #1F2937;
}
.card-right {
  font-size: 14px;
}
.subject-title-name strong {
  font-size: 16px;
}
.no-courses {
  padding: 40px 0;
}

/* 动效 */
.animate-fade {
  animation: fadeIn 0.35s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
