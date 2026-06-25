<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { getHomeworkOverview } from "../../api/homework";
import { getTeacherClasses } from "../../api/scores";
import { Warning, TrendCharts, Checked, DataAnalysis } from "@element-plus/icons-vue";

interface HomeworkOverviewItem {
  homework_id: number;
  title: string;
  subject: string;
  class_id: number;
  class_name: string;
  teacher_name: string;
  total_students: number;
  submitted_count: number;
  submission_rate: number;
  average_grade: number | null;
  due_date: string;
  created_at: string;
}

interface ClassOption {
  id: number;
  name: string;
}

const overviewList = ref<HomeworkOverviewItem[]>([]);
const classes = ref<ClassOption[]>([]);
const loading = ref(false);

const filterClassId = ref<number | null>(null);
const filterSubject = ref<string>("");

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const stats = computed(() => {
  const total = overviewList.value.length;
  
  // Calculate average submission rate
  const totalStudents = overviewList.value.reduce((acc, curr) => acc + curr.total_students, 0);
  const totalSubmitted = overviewList.value.reduce((acc, curr) => acc + curr.submitted_count, 0);
  const avgSubRate = totalStudents > 0 ? ((totalSubmitted / totalStudents) * 100).toFixed(1) : "0.0";
  
  // Count anomalies (submission rate < 70%)
  const anomalies = overviewList.value.filter((h) => h.submission_rate < 70).length;

  return { total, avgSubRate, anomalies };
});

const filteredOverview = computed(() => {
  return overviewList.value.filter((h) => {
    const matchClass = !filterClassId.value || h.class_id === filterClassId.value;
    const matchSubj = !filterSubject.value || h.subject === filterSubject.value;
    return matchClass && matchSubj;
  });
});

async function loadData() {
  loading.value = true;
  try {
    const [overviewRes, classesRes]: any = await Promise.all([
      getHomeworkOverview(),
      getTeacherClasses(),
    ]);
    overviewList.value = overviewRes.data || [];
    classes.value = classesRes.data?.classes || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取教务作业概况失败");
  } finally {
    loading.value = false;
  }
}

function formatTime(timeStr: string) {
  if (!timeStr) return "-";
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="homework-overview" v-loading="loading">
    <!-- 顶部数据大屏统计 -->
    <div class="admin-stats">
      <div class="astat-card">
        <div class="astat-icon blue"><TrendCharts /></div>
        <div class="astat-info">
          <span class="astat-label">已布置作业数</span>
          <span class="astat-value">{{ stats.total }} <small>项</small></span>
        </div>
      </div>
      <div class="astat-card">
        <div class="astat-icon green"><Checked /></div>
        <div class="astat-info">
          <span class="astat-label">全校平均提交率</span>
          <span class="astat-value">{{ stats.avgSubRate }}%</span>
        </div>
      </div>
      <div class="astat-card" :class="{ warning: stats.anomalies > 0 }">
        <div class="astat-icon orange"><Warning /></div>
        <div class="astat-info">
          <span class="astat-label">提交率异常项 (&lt;70%)</span>
          <span class="astat-value danger-text">{{ stats.anomalies }} <small>项</small></span>
        </div>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div class="filter-panel">
      <el-form :inline="true" size="default">
        <el-form-item label="班级">
          <el-select v-model="filterClassId" placeholder="全部班级" clearable style="width: 160px">
            <el-option 
              v-for="c in classes" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学科">
          <el-select v-model="filterSubject" placeholder="全部学科" clearable style="width: 140px">
            <el-option 
              v-for="(val, key) in SUBJECTS" 
              :key="key" 
              :label="val" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表 -->
    <div class="table-card">
      <el-table :data="filteredOverview" style="width: 100%" class="custom-table">
        <el-table-column prop="class_name" label="班级" width="130" />
        <el-table-column prop="subject" label="科目" width="100">
          <template #default="{ row }">
            {{ SUBJECTS[row.subject] || row.subject }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="作业标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="teacher_name" label="任课教师" width="110" />
        <el-table-column label="已交 / 总人数" width="130">
          <template #default="{ row }">
            <span>{{ row.submitted_count }} / {{ row.total_students }}</span>
          </template>
        </el-table-column>
        <el-table-column label="提交率" width="120">
          <template #default="{ row }">
            <span :class="['rate-text', { 'anomaly-warning': row.submission_rate < 70 }]">
              {{ row.submission_rate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="平均得分" width="100">
          <template #default="{ row }">
            <span>{{ row.average_grade !== null ? row.average_grade : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="截止时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.due_date) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.homework-overview {
  width: 100%;
}

/* 顶部统计 */
.admin-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.astat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}
.astat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.astat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.astat-icon.blue {
  background: rgba(51, 78, 172, 0.1);
  color: var(--color-primary);
}
.astat-icon.green {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
.astat-icon.orange {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}
.astat-card.warning {
  border-color: var(--color-danger);
  background: rgba(239, 68, 68, 0.02);
}
.astat-info {
  display: flex;
  flex-direction: column;
}
.astat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.astat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
}
.astat-value small {
  font-size: 13px;
  font-weight: normal;
  color: var(--color-text-secondary);
}
.danger-text {
  color: var(--color-danger);
}

/* 筛选面板 */
.filter-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  padding: 14px 18px 0;
  margin-bottom: 20px;
}

/* 数据表 */
.table-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.rate-text {
  font-weight: 700;
  color: var(--color-success);
}
.rate-text.anomaly-warning {
  color: var(--color-danger);
  padding: 2px 6px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
}
</style>
