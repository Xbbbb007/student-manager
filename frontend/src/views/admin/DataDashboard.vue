<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { ElMessage } from "element-plus";
import { Chart, registerables } from "chart.js";
import http from "../../api/http";
import { listClassesApi, type ClassInfo } from "../../api/classes";
import { getExams } from "../../api/scores";
import { Checked, Monitor, Medal, Notebook, Download } from "@element-plus/icons-vue";

Chart.register(...registerables);

const classes = ref<ClassInfo[]>([]);
const exams = ref<any[]>([]);
const selectedClassId = ref<number | null>(null);
const selectedExamId = ref<number | null>(null);
const loading = ref(false);

const stats = ref({
  attendance_rate: 98.4,
  homework_rate: 92.1,
  score_avg: 84.5,
  mistakes_cnt: 1420
});

// Chart instances are directly initialized

async function loadFilterOptions() {
  try {
    const [classesRes, examsRes]: any = await Promise.all([
      listClassesApi(),
      getExams()
    ]);
    classes.value = classesRes.data || [];
    exams.value = examsRes.data || [];
    if (classes.value.length > 0) selectedClassId.value = classes.value[0].id;
    if (exams.value.length > 0) selectedExamId.value = exams.value[0].id;
  } catch (error) {
    console.error(error);
  }
}

async function handleExport() {
  if (!selectedClassId.value || !selectedExamId.value) {
    ElMessage.warning("请选择要导出的班级和考试");
    return;
  }
  
  loading.value = true;
  try {
    const res = await http.get('/scores/export', {
      params: { exam_id: selectedExamId.value, class_id: selectedClassId.value },
      responseType: 'blob'
    });
    
    const blob = new Blob([res as any], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Get class name
    const clsName = classes.value.find(c => c.id === selectedClassId.value)?.name || "班级";
    const examName = exams.value.find(e => e.id === selectedExamId.value)?.name || "考试";
    
    link.setAttribute('download', `${clsName}_${examName}_成绩表.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    ElMessage.success("成绩表导出成功！");
  } catch (error) {
    console.error(error);
    ElMessage.error("导出成绩表失败，当前筛选条件可能无成绩记录");
  } finally {
    loading.value = false;
  }
}

function initCharts() {
  // 1. Attendance line chart
  const attCtx = document.getElementById("attendanceTrendChart") as HTMLCanvasElement;
  if (attCtx) {
    new Chart(attCtx, {
      type: "line",
      data: {
        labels: ["周一", "周二", "周三", "周四", "周五"],
        datasets: [{
          label: "全校出勤率 (%)",
          data: [98.1, 98.4, 97.9, 98.6, 99.1],
          borderColor: "#334EAC",
          backgroundColor: "rgba(51, 78, 172, 0.1)",
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  // 2. Homework bar chart
  const hwCtx = document.getElementById("homeworkStatsChart") as HTMLCanvasElement;
  if (hwCtx) {
    new Chart(hwCtx, {
      type: "bar",
      data: {
        labels: ["语文", "数学", "英语", "科学", "道德与法治"],
        datasets: [
          {
            label: "布置量 (次)",
            data: [12, 10, 8, 5, 4],
            backgroundColor: "#7096D1"
          },
          {
            label: "提交率 (%)",
            data: [94.5, 92.1, 95.8, 89.2, 91.0],
            backgroundColor: "#10B981"
          }
        ]
      },
      options: {
        responsive: true
      }
    });
  }

  // 3. Subject radar chart
  const subCtx = document.getElementById("subjectAveragesChart") as HTMLCanvasElement;
  if (subCtx) {
    new Chart(subCtx, {
      type: "radar",
      data: {
        labels: ["语文", "数学", "英语", "科学", "道德与法治"],
        datasets: [{
          label: "全校均分",
          data: [85, 82, 88, 78, 89],
          borderColor: "#E8A838",
          backgroundColor: "rgba(232, 168, 56, 0.2)",
          pointBackgroundColor: "#E8A838"
        }]
      },
      options: {
        responsive: true
      }
    });
  }
}

onMounted(async () => {
  await loadFilterOptions();
  nextTick(() => {
    initCharts();
  });
});
</script>

<template>
  <div class="data-dashboard" v-loading="loading">
    <div class="header-action-bar">
      <h2>教务全局数据大屏</h2>
      <div class="export-controls">
        <el-select v-model="selectedClassId" placeholder="选择班级" style="width: 140px; margin-right: 8px">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="selectedExamId" placeholder="选择考试" style="width: 180px; margin-right: 8px">
          <el-option v-for="e in exams" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
        <el-button type="primary" :icon="Download" @click="handleExport">导出 Excel 成绩</el-button>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="icon-box att"><el-icon><Checked /></el-icon></div>
        <div class="info">
          <span class="label">全校平均出勤率</span>
          <span class="val">{{ stats.attendance_rate }}%</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="icon-box hw"><el-icon><Monitor /></el-icon></div>
        <div class="info">
          <span class="label">作业提交率</span>
          <span class="val">{{ stats.homework_rate }}%</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="icon-box avg"><el-icon><Medal /></el-icon></div>
        <div class="info">
          <span class="label">考试成绩均分</span>
          <span class="val">{{ stats.score_avg }} 分</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="icon-box mis"><el-icon><Notebook /></el-icon></div>
        <div class="info">
          <span class="label">累积录入错题数</span>
          <span class="val">{{ stats.mistakes_cnt }} 道</span>
        </div>
      </div>
    </div>

    <!-- Charts Layout Grid -->
    <div class="charts-layout">
      <!-- Attendance trends -->
      <div class="chart-container">
        <h3>全校每日考勤率趋势</h3>
        <canvas id="attendanceTrendChart"></canvas>
      </div>
      
      <!-- Homework stats -->
      <div class="chart-container">
        <h3>各学科作业布置与提交对比</h3>
        <canvas id="homeworkStatsChart"></canvas>
      </div>

      <!-- Subject averages radar -->
      <div class="chart-container span-2">
        <h3>各学科全校均分分布图</h3>
        <div class="radar-wrapper">
          <canvas id="subjectAveragesChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.data-dashboard {
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
.export-controls {
  display: flex;
  align-items: center;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}
.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
}
.icon-box.att { background-color: #334EAC; }
.icon-box.hw { background-color: #10B981; }
.icon-box.avg { background-color: #E8A838; }
.icon-box.mis { background-color: #EF4444; }

.info {
  display: flex;
  flex-direction: column;
}
.info .label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.info .val {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
}

/* Charts Grid */
.charts-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.chart-container {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.chart-container h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 8px;
}
.span-2 {
  grid-column: span 2;
}
.radar-wrapper {
  max-width: 320px;
  margin: 0 auto;
}
</style>
