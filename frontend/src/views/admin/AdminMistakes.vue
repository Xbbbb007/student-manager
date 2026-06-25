<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getAdminMistakeTrends } from "../../api/mistake";
import { PieChart, TrendCharts } from "@element-plus/icons-vue";

interface TrendItem {
  subject: string;
  subject_name: string;
  count: number;
}

const trends = ref<TrendItem[]>([]);
const loading = ref(true);

const SUBJECT_COLORS: Record<string, string> = {
  chinese: "#334EAC",
  math: "#10B981",
  english: "#F59E0B",
  science: "#8B5CF6",
  ethics: "#EC4899",
};

function getSubjectColor(subject: string) {
  return SUBJECT_COLORS[subject] || "#6B7280";
}

async function loadData() {
  loading.value = true;
  try {
    const res: any = await getAdminMistakeTrends();
    trends.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取全校错题趋势数据失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="admin-mistakes" v-loading="loading">
    <div class="header-action">
      <h2>全校错题分析与学科趋势</h2>
    </div>

    <div v-if="trends.length === 0" class="empty-state">
      <el-empty description="当前暂无全校错题数据" />
    </div>

    <div v-else class="trends-content">
      <!-- 统计简报 -->
      <div class="stat-summary-box">
        <div class="summary-card">
          <div class="card-icon"><PieChart /></div>
          <div class="card-info">
            <span class="lbl">录入错题学科数</span>
            <span class="val">{{ trends.length }} <small>科</small></span>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon"><TrendCharts /></div>
          <div class="card-info">
            <span class="lbl">全校总错题量</span>
            <span class="val">
              {{ trends.reduce((acc, curr) => acc + curr.count, 0) }} <small>道</small>
            </span>
          </div>
        </div>
      </div>

      <!-- 学科分布列表 / 进度条展示 -->
      <div class="subject-trend-list">
        <h3>各学科错题分布占比</h3>
        <div class="list-wrapper">
          <div 
            v-for="item in trends" 
            :key="item.subject"
            class="trend-row"
          >
            <div class="row-label">
              <span 
                class="color-dot" 
                :style="{ backgroundColor: getSubjectColor(item.subject) }"
              ></span>
              <span class="subj-name">{{ item.subject_name }}</span>
            </div>
            <div class="row-progress">
              <el-progress 
                :percentage="trends.reduce((acc, curr) => acc + curr.count, 0) ? Math.round((item.count / trends.reduce((acc, curr) => acc + curr.count, 0)) * 100) : 0"
                :color="getSubjectColor(item.subject)"
              />
            </div>
            <div class="row-value">
              <strong>{{ item.count }}</strong> 道错题
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-mistakes {
  width: 100%;
}
.header-action {
  margin-bottom: 24px;
}
.header-action h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.stat-summary-box {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}
.summary-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
}
.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: rgba(51, 78, 172, 0.1);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.card-info {
  display: flex;
  flex-direction: column;
}
.card-info .lbl {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.card-info .val {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
}
.card-info .val small {
  font-size: 12px;
  font-weight: normal;
  color: var(--color-text-secondary);
}

.subject-trend-list {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
}
.subject-trend-list h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 20px;
}
.list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.trend-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.row-label {
  width: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.subj-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.row-progress {
  flex: 1;
}
.row-value {
  width: 120px;
  text-align: right;
  font-size: 13px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.row-value strong {
  color: var(--color-text);
  font-size: 15px;
}

.empty-state {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
  padding: 60px 0;
}
</style>
