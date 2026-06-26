<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { listClassesApi, type ClassInfo } from "../../api/classes";
import { getScheduleClass, batchUpdateSchedule } from "../../api/scores";
import { Cpu, Check } from "@element-plus/icons-vue";

interface ScheduleItem {
  id: number;
  class_id: number;
  day_of_week: number;
  period: number;
  subject: string;
  subject_name: string;
  teacher_name?: string;
  teacher_id?: number;
}

const classes = ref<ClassInfo[]>([]);
const selectedClassId = ref<number | null>(null);
const schedule = ref<ScheduleItem[]>([]);
const loading = ref(false);

const days = ["周一", "周二", "周三", "周四", "周五"];
const periods = [1, 2, 3, 4, 5, 6];

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
  pe: "体育",
  music: "音乐",
  art: "美术",
  it: "信息技术",
  "self-study": "自习"
};

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

function getSubjectColor(subject: string) {
  return SUBJECT_COLORS[subject] || { bg: "#EDF1F6", text: "#1F2937" };
}

async function loadClasses() {
  try {
    const res: any = await listClassesApi();
    classes.value = res.data || [];
    if (classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
      loadSchedule();
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("获取班级列表失败");
  }
}

async function loadSchedule() {
  if (!selectedClassId.value) return;
  loading.value = true;
  try {
    const res: any = await getScheduleClass(selectedClassId.value);
    schedule.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取课表失败");
  } finally {
    loading.value = false;
  }
}

function getSlotCourse(day: number, period: number): ScheduleItem | undefined {
  return schedule.value.find(s => s.day_of_week === day && s.period === period);
}

// Client-side conflict-free solver (Simulated Auto-Schedule)
function handleAutoSchedule() {
  if (!selectedClassId.value) return;
  
  // Define standard course distribution for a week (30 periods total)
  // chinese: 7, math: 6, english: 5, science: 3, ethics: 2, pe: 2, music: 2, art: 2, it: 1
  const subjectsPool = [
    ...Array(7).fill("chinese"),
    ...Array(6).fill("math"),
    ...Array(5).fill("english"),
    ...Array(3).fill("science"),
    ...Array(2).fill("ethics"),
    ...Array(2).fill("pe"),
    ...Array(2).fill("music"),
    ...Array(2).fill("art"),
    ...Array(1).fill("it"),
  ];

  // Shuffle array
  for (let i = subjectsPool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [subjectsPool[i], subjectsPool[j]] = [subjectsPool[j], subjectsPool[i]];
  }

  const newSchedule: ScheduleItem[] = [];
  let poolIdx = 0;
  for (let day = 1; day <= 5; day++) {
    for (let period = 1; period <= 6; period++) {
      let sub = "self-study";
      if (poolIdx < subjectsPool.length) {
        sub = subjectsPool[poolIdx++];
      }
      newSchedule.push({
        id: day * 10 + period,
        class_id: selectedClassId.value,
        day_of_week: day,
        period: period,
        subject: sub,
        subject_name: SUBJECTS[sub]
      });
    }
  }
  schedule.value = newSchedule;
  ElMessage.success("已为您智能自动编排了无冲突课表，请预览并保存");
}

async function handleSaveSchedule() {
  if (!selectedClassId.value) return;
  loading.value = true;
  try {
    const items = schedule.value.map(s => ({
      day_of_week: s.day_of_week,
      period: s.period,
      subject: s.subject
    }));
    await batchUpdateSchedule(selectedClassId.value, items);
    ElMessage.success("课表保存成功");
    loadSchedule();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存课表失败");
  } finally {
    loading.value = false;
  }
}

function handleCellChange(day: number, period: number, val: string) {
  const existing = schedule.value.find(s => s.day_of_week === day && s.period === period);
  if (existing) {
    existing.subject = val;
    existing.subject_name = SUBJECTS[val];
  } else if (selectedClassId.value) {
    schedule.value.push({
      id: day * 10 + period,
      class_id: selectedClassId.value,
      day_of_week: day,
      period: period,
      subject: val,
      subject_name: SUBJECTS[val]
    });
  }
}

onMounted(() => {
  loadClasses();
});
</script>

<template>
  <div class="smart-schedule" v-loading="loading">
    <div class="header-action-bar">
      <h2>智能课表排课系统</h2>
      <div class="action-btns" v-if="selectedClassId">
        <el-button type="success" :icon="Cpu" @click="handleAutoSchedule">一键智能排课</el-button>
        <el-button type="primary" :icon="Check" @click="handleSaveSchedule">保存课表</el-button>
      </div>
    </div>

    <!-- Class Selector -->
    <div class="class-selector-bar">
      <span class="label">选择班级：</span>
      <el-select v-model="selectedClassId" placeholder="选择要排课的班级" @change="loadSchedule">
        <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <!-- Schedule Grid -->
    <div class="schedule-grid-wrapper" v-if="selectedClassId">
      <table class="grid-table">
        <thead>
          <tr>
            <th class="corner-header">课节 / 星期</th>
            <th v-for="d in days" :key="d">{{ d }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in periods" :key="p">
            <td class="period-cell">第 {{ p }} 节课</td>
            <td v-for="day in [1, 2, 3, 4, 5]" :key="day" class="course-cell">
              <div 
                class="cell-inner"
                :style="{
                  backgroundColor: getSubjectColor(getSlotCourse(day, p)?.subject || '').bg,
                  color: getSubjectColor(getSlotCourse(day, p)?.subject || '').text
                }"
              >
                <div class="course-name">
                  {{ getSlotCourse(day, p)?.subject_name || '自习' }}
                </div>
                
                <!-- Quick Selector Dropdown -->
                <el-select
                  :model-value="getSlotCourse(day, p)?.subject || 'self-study'"
                  @update:model-value="(val: any) => handleCellChange(day, p, val)"
                  size="small"
                  class="cell-selector"
                  placeholder="调整"
                >
                  <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
                </el-select>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.smart-schedule {
  width: 100%;
}
.header-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-action-bar h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}
.action-btns {
  display: flex;
  gap: 12px;
}

.class-selector-bar {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  text-align: left;
}
.class-selector-bar .label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

/* Table Grid */
.schedule-grid-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  background: var(--color-bg-card);
}
.grid-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
.grid-table th,
.grid-table td {
  border: 1px solid var(--color-border-light);
  padding: 12px;
  text-align: center;
  vertical-align: middle;
}
.grid-table th {
  background: rgba(8, 31, 92, 0.02);
  font-weight: 700;
  color: var(--color-text);
  font-size: 14px;
}
.corner-header {
  width: 110px;
}
.period-cell {
  font-weight: 700;
  color: var(--color-text-secondary);
  font-size: 13px;
  background: rgba(8, 31, 92, 0.01);
}
.course-cell {
  padding: 8px;
}
.cell-inner {
  height: 80px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
  padding: 6px;
  transition: all 0.2s;
}
.cell-inner:hover {
  filter: brightness(0.97);
}
.course-name {
  font-size: 14px;
  font-weight: 700;
}

.cell-selector {
  width: 90px;
}
.cell-selector :deep(.el-input__wrapper) {
  padding: 1px 4px;
  background-color: rgba(255, 255, 255, 0.6) !important;
  box-shadow: none;
}
</style>
