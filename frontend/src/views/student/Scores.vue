<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { getScoreTrend, getClassRanking } from "../../api/scores";
import Chart from "chart.js/auto";

const props = defineProps<{ activeTab: string }>();

const subjectKeys = [
  "chinese",
  "math",
  "english",
  "science",
  "ethics",
] as const;
const subjectNames: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const BAR_DEFAULT = "#d49a9a";
const BAR_HOVER = "#bb7b7b";

interface ScoreItem {
  subject: string;
  score: number;
  class_rank: number | null;
  school_rank: number | null;
}

interface RankItem {
  rank: number;
  student_id: number;
  student_name: string;
  total: number;
  rank_change: number | null;
  score_change: number | null;
}

const examLabels = ref<string[]>([]);
const scores = ref<Record<string, number[]>>({
  chinese: [],
  math: [],
  english: [],
  science: [],
  ethics: [],
});
const totalScores = ref<number[]>([]);
const classRank = ref<(number | null)[]>([]);
const schoolRank = ref<(number | null)[]>([]);
const subjectClassRanks = ref<Record<string, (number | null)[]>>({
  chinese: [],
  math: [],
  english: [],
  science: [],
  ethics: [],
});
const subjectSchoolRanks = ref<Record<string, (number | null)[]>>({
  chinese: [],
  math: [],
  english: [],
  science: [],
  ethics: [],
});
const rankingData = ref<RankItem[]>([]);

const studentInfo = ref({ name: "", no: "", className: "" });
const studentId = ref(0);
const latestScores = ref<Record<string, number>>({});
const latestTotal = ref(0);

const currentMainKey = ref("total");

let mainChart: Chart | null = null;
let radarChart: Chart | null = null;

const mainCanvas = ref<HTMLCanvasElement | null>(null);
const radarCanvas = ref<HTMLCanvasElement | null>(null);

const radarVisible = ref({ current: true, prev: true });

const centeredRanking = computed(() => {
  const data = rankingData.value;
  if (!data.length) return [];
  const idx = data.findIndex((r) => r.student_id === studentId.value);
  const meIdx = idx >= 0 ? idx : 0;
  const start = Math.max(0, meIdx - 3);
  const end = Math.min(data.length, meIdx + 4);
  return data.slice(start, end);
});

function getBarData(key: string) {
  const raw = key === "total" ? totalScores.value : scores.value[key];
  if (!raw.length) return [];
  const min = Math.min(...raw);
  const max = Math.max(...raw);
  const range = max - min || 1;
  const baseline = Math.max(0, min - range * 0.5 - 10);
  return raw.map((v) => v - baseline);
}

function getBarMax(key: string) {
  const raw = key === "total" ? totalScores.value : scores.value[key];
  if (!raw.length) return 100;
  const min = Math.min(...raw);
  const max = Math.max(...raw);
  const range = max - min || 1;
  const baseline = Math.max(0, min - range * 0.5 - 10);
  return max - baseline + range * 0.3;
}

function getRankMax(values: (number | null)[]): number {
  const valid = values.filter((v): v is number => v != null);
  if (!valid.length) return 50;
  const maxVal = Math.max(...valid);
  // Round up to next multiple of 10 for clean tick marks
  return Math.ceil(maxVal / 10) * 10;
}

function getRankStepSize(maxVal: number): number {
  if (maxVal <= 20) return 5;
  if (maxVal <= 50) return 10;
  if (maxVal <= 100) return 20;
  return 50;
}

function buildMainDatasets(key: string) {
  const rankData =
    key === "total"
      ? { classRank: classRank.value, schoolRank: schoolRank.value }
      : {
          classRank: subjectClassRanks.value[key] || [],
          schoolRank: subjectSchoolRanks.value[key] || [],
        };

  return [
    {
      label: key === "total" ? "总分" : subjectNames[key],
      data: getBarData(key),
      backgroundColor: BAR_DEFAULT,
      hoverBackgroundColor: BAR_HOVER,
      borderRadius: 0,
      borderSkipped: false,
      barPercentage: 0.45,
      yAxisID: "bar",
      order: 2,
    },
    {
      label: "班排名",
      data: rankData.classRank,
      type: "line" as const,
      borderColor: "#334EAC",
      backgroundColor: "transparent",
      pointBackgroundColor: "#334EAC",
      pointBorderColor: "#fff",
      pointBorderWidth: 2.5,
      pointRadius: 5,
      pointHoverRadius: 8,
      borderWidth: 2.5,
      tension: 0.4,
      fill: false,
      yAxisID: "yLeft",
      order: 1,
    },
    {
      label: "校排名",
      data: rankData.schoolRank,
      type: "line" as const,
      borderColor: "#E8A838",
      backgroundColor: "transparent",
      pointBackgroundColor: "#E8A838",
      pointBorderColor: "#fff",
      pointBorderWidth: 2.5,
      pointRadius: 5,
      pointHoverRadius: 8,
      borderWidth: 2.5,
      tension: 0.4,
      fill: false,
      yAxisID: "yRight",
      order: 1,
    },
  ];
}

function initMainChart() {
  if (!mainCanvas.value) return;
  const ctx = mainCanvas.value.getContext("2d")!;
  mainChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: examLabels.value,
      datasets: buildMainDatasets("total"),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "circle",
            padding: 16,
            font: { size: 11, weight: "600" },
            color: "#6B7280",
          },
        },
        tooltip: {
          backgroundColor: "rgba(255,255,255,0.97)",
          titleColor: "#1F2937",
          bodyColor: "#6B7280",
          borderColor: "#E5E7EB",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 14,
          titleFont: { size: 13, weight: "bold" },
          bodyFont: { size: 12 },
          bodySpacing: 6,
          usePointStyle: true,
          callbacks: {
            title: (items: any) => items[0].label,
            afterTitle: (items: any) => {
              const idx = items[0].dataIndex;
              const key = currentMainKey.value;
              const raw =
                key === "total" ? totalScores.value : scores.value[key];
              return (
                (key === "total" ? "总分" : subjectNames[key]) +
                "：" +
                raw[idx] +
                " 分"
              );
            },
            label: (ctx: any) => {
              const l = ctx.dataset.label;
              const v = ctx.parsed.y;
              if (l === "班排名") return `  班排名：第 ${v} 名`;
              if (l === "校排名") return `  校排名：第 ${v} 名`;
              return null;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(148,163,184,0.06)", lineWidth: 1 },
          ticks: {
            font: { size: 12, weight: "500" },
            color: "#9CA3AF",
            padding: 8,
          },
        },
        bar: {
          display: false,
          min: 0,
          max: getBarMax("total"),
          stacked: false,
        },
        yLeft: {
          position: "left",
          title: {
            display: true,
            text: "班排名",
            color: "#334EAC",
            font: { size: 12, weight: "bold" },
            padding: 10,
          },
          reverse: true,
          min: 0,
          max: getRankMax(classRank.value),
          grid: { color: "rgba(148,163,184,0.08)", lineWidth: 1 },
          ticks: {
            stepSize: getRankStepSize(getRankMax(classRank.value)),
            padding: 8,
            color: "#334EAC",
            callback: (v: any) => (v > 0 ? v + "名" : ""),
          },
          border: { display: false },
        },
        yRight: {
          position: "right",
          title: {
            display: true,
            text: "校排名",
            color: "#E8A838",
            font: { size: 12, weight: "bold" },
            padding: 10,
          },
          reverse: true,
          min: 0,
          max: getRankMax(schoolRank.value),
          grid: { drawOnChartArea: false },
          ticks: {
            stepSize: getRankStepSize(getRankMax(schoolRank.value)),
            padding: 8,
            color: "#E8A838",
            callback: (v: any) => (v > 0 ? v + "名" : ""),
          },
          border: { display: false },
        },
      },
      animation: { duration: 800, easing: "easeOutQuart" },
      transitions: {
        active: { animation: { duration: 500, easing: "easeInOutCubic" } }
      },
    },
  });
}

function switchSubject(key: string) {
  currentMainKey.value = key;
  if (!mainChart) return;

  const rankData =
    key === "total"
      ? { classRank: classRank.value, schoolRank: schoolRank.value }
      : {
          classRank: subjectClassRanks.value[key] || [],
          schoolRank: subjectSchoolRanks.value[key] || [],
        };

  mainChart.data.datasets[0].data = getBarData(key);
  mainChart.data.datasets[0].label = key === "total" ? "总分" : subjectNames[key];
  mainChart.data.datasets[1].data = rankData.classRank;
  mainChart.data.datasets[2].data = rankData.schoolRank;
  mainChart.options.scales!.bar!.max = getBarMax(key);

  // 动态更新排名 Y 轴范围
  const classMax = getRankMax(rankData.classRank);
  const schoolMax = getRankMax(rankData.schoolRank);
  mainChart.options.scales!.yLeft!.max = classMax;
  mainChart.options.scales!.yLeft!.ticks!.stepSize = getRankStepSize(classMax);
  mainChart.options.scales!.yRight!.max = schoolMax;
  mainChart.options.scales!.yRight!.ticks!.stepSize = getRankStepSize(schoolMax);

  mainChart.update();
}

function initRadarChart() {
  if (!radarCanvas.value) return;
  const ctx = radarCanvas.value.getContext("2d")!;
  const lastExam = examLabels.value.length - 1;
  const prevExam = Math.max(0, lastExam - 1);

  const currentData = subjectKeys.map((k) => scores.value[k][lastExam] || 0);
  const prevData = subjectKeys.map((k) => scores.value[k][prevExam] || 0);

  radarChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: subjectKeys.map((k) => subjectNames[k]),
      datasets: [
        {
          label: "本次成绩",
          data: currentData,
          backgroundColor: "rgba(51,78,172,0.15)",
          borderColor: "rgba(51,78,172,0.8)",
          borderWidth: 2.5,
          pointBackgroundColor: "#334EAC",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 7,
        },
        {
          label: "上次成绩",
          data: prevData,
          backgroundColor: "rgba(112,150,209,0.15)",
          borderColor: "rgba(112,150,209,0.7)",
          borderWidth: 2.5,
          pointBackgroundColor: "#7096D1",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 7,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(255,255,255,0.97)",
          titleColor: "#1F2937",
          bodyColor: "#6B7280",
          borderColor: "#E5E7EB",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          titleFont: { size: 13, weight: "bold" },
          bodyFont: { size: 12 },
          usePointStyle: true,
          callbacks: {
            title: (ctx: any) => ctx[0].label,
            label: (ctx: any) => `  ${ctx.dataset.label}：${ctx.parsed.r} 分`,
          },
        },
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 25, display: false },
          grid: { color: "rgba(148,163,184,0.12)" },
          angleLines: { color: "rgba(148,163,184,0.10)" },
          pointLabels: {
            color: "#475569",
            font: { size: 12, weight: "bold" },
            padding: 12,
          },
        },
      },
      animation: { duration: 600, easing: "easeOutQuart" },
      transitions: {
        active: {
          animation: { duration: 500, easing: "easeInOutCubic" }
        }
      },
    },
  });
}

function toggleRadarDataset(index: number) {
  if (!radarChart) return;
  const meta = radarChart.getDatasetMeta(index);
  meta.hidden = !meta.hidden;
  if (index === 0) radarVisible.value.current = !radarVisible.value.current;
  else radarVisible.value.prev = !radarVisible.value.prev;
  radarChart.update();
}

onMounted(async () => {
  try {
    const res: any = await getScoreTrend();
    const data = res.data;
    examLabels.value = data.exam_labels || [];
    scores.value = data.scores || {};
    totalScores.value = data.total_scores || [];
    classRank.value = data.class_rank || [];
    schoolRank.value = data.school_rank || [];
    subjectClassRanks.value = data.subject_class_ranks || {};
    subjectSchoolRanks.value = data.subject_school_ranks || {};

    studentInfo.value = {
      name: data.student_name || '',
      no: data.student_no || '',
      className: data.class_name || '',
    };
    studentId.value = data.student_id || 0;

    const lastIdx = (data.exam_labels || []).length - 1;
    if (lastIdx >= 0) {
      const s: Record<string, number> = {};
      subjectKeys.forEach((k) => {
        s[k] = data.scores?.[k]?.[lastIdx] ?? 0;
      });
      latestScores.value = s;
      latestTotal.value = data.total_scores?.[lastIdx] ?? 0;
    }

    nextTick(() => {
      initMainChart();
      initRadarChart();
    });

    const latestExamId = data.latest_exam_id;
    if (latestExamId) {
      try {
        const rankRes: any = await getClassRanking(latestExamId);
        rankingData.value = rankRes.data?.rankings || [];
      } catch (e2) {
        console.error("加载排名数据失败", e2);
      }
    }
  } catch (e) {
    console.error("加载成绩数据失败", e);
  }
});
</script>

<template>
  <div class="scores-content">
    <div class="chart-ranking-row">
      <!-- 主图表 -->
      <div class="main-chart-card fade-in">
        <div class="section-header">
          <div>
            <div class="section-title">成绩变化趋势</div>
          </div>
          <div class="select-wrap">
            <select
              :value="currentMainKey"
              @change="
                switchSubject(($event.target as HTMLSelectElement).value)
              "
            >
              <option value="total">总分</option>
              <option v-for="k in subjectKeys" :key="k" :value="k">
                {{ subjectNames[k] }}
              </option>
            </select>
            <div class="arrow">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          </div>
        </div>
        <div class="main-chart-area">
          <canvas ref="mainCanvas"></canvas>
        </div>
      </div>

      <!-- 个人信息 -->
      <div class="profile-section fade-in">
        <div class="profile-title">个人信息</div>
        <table class="profile-info-table">
          <tr><td class="pil">姓名</td><td class="piv">{{ studentInfo.name }}</td></tr>
          <tr><td class="pil">学号</td><td class="piv">{{ studentInfo.no }}</td></tr>
          <tr><td class="pil">总分</td><td class="piv score-highlight">{{ latestTotal }}</td></tr>
          <tr v-for="k in subjectKeys" :key="k">
            <td class="pil">{{ subjectNames[k] }}</td>
            <td class="piv">{{ latestScores[k] ?? '-' }}</td>
          </tr>
        </table>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="triple-columns">
      <div class="content-left">
        <!-- 雷达图 -->
        <div class="radar-section fade-in">
          <div class="radar-header">
            <span class="radar-title">学科能力雷达</span>
          </div>
          <div class="radar-area">
            <canvas ref="radarCanvas"></canvas>
          </div>
          <div class="radar-legend">
            <div
              :class="['radar-legend-item', { hidden: !radarVisible.current }]"
              @click="toggleRadarDataset(0)"
            >
              <span class="legend-dot" style="background: #334eac"></span
              >本次成绩
            </div>
            <div
              :class="['radar-legend-item', { hidden: !radarVisible.prev }]"
              @click="toggleRadarDataset(1)"
            >
              <span class="legend-dot" style="background: #7096d1"></span
              >上次成绩
            </div>
          </div>
        </div>

        <!-- 班级排名 -->
        <div class="ranking-section fade-in">
          <div class="ranking-title">班级排名</div>
          <div class="ranking-list">
            <div class="ranking-item ranking-header">
              <div class="ranking-left">
                <span class="ranking-rank">排名</span>
                <span class="ranking-name">姓名</span>
                <span class="ranking-rank-change">变化</span>
              </div>
              <div class="ranking-right">
                <span class="ranking-score">分数</span>
                <span class="ranking-change">变化</span>
              </div>
            </div>
            <div
              v-for="item in centeredRanking"
              :key="item.student_id"
              :class="['ranking-item', { 'is-me': item.student_id === studentId }]"
            >
              <div class="ranking-left">
                <span class="ranking-rank">{{ item.rank }}</span>
                <span class="ranking-name">{{ item.student_name }}</span>
                <span
                  class="ranking-rank-change"
                  :class="{
                    up: item.rank_change && item.rank_change > 0,
                    down: item.rank_change && item.rank_change < 0,
                    flat: !item.rank_change,
                  }"
                >
                  <template v-if="item.rank_change && item.rank_change > 0">
                    <svg viewBox="0 0 8 8">
                      <path d="M4 1L7 5H1Z" fill="currentColor" /></svg
                    >{{ item.rank_change }}
                  </template>
                  <template
                    v-else-if="item.rank_change && item.rank_change < 0"
                  >
                    <svg viewBox="0 0 8 8">
                      <path d="M4 7L7 3H1Z" fill="currentColor" /></svg
                    >{{ Math.abs(item.rank_change) }}
                  </template>
                  <template v-else>—</template>
                </span>
              </div>
              <div class="ranking-right">
                <span class="ranking-score">{{ item.total }}</span>
                <span
                  class="ranking-change"
                  :class="{
                    up: item.score_change && item.score_change > 0,
                    down: item.score_change && item.score_change < 0,
                    flat: !item.score_change,
                  }"
                >
                  <template v-if="item.score_change && item.score_change > 0"
                    >+{{ item.score_change }}</template
                  >
                  <template
                    v-else-if="item.score_change && item.score_change < 0"
                    >{{ item.score_change }}</template
                  >
                  <template v-else>—</template>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 对话区域（预留） -->
      <div class="ai-placeholder fade-in">
        <div class="ai-placeholder-inner">
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"
            />
            <path d="M9 21v1a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1" />
            <line x1="10" y1="10" x2="10.01" y2="10" />
            <line x1="14" y1="10" x2="14.01" y2="10" />
          </svg>
          <span class="ai-placeholder-text">AI 智能助手</span>
          <span class="ai-placeholder-sub">即将上线</span>
        </div>
      </div>
    </div>

    <!-- 详细表格 -->
    <div class="detail-section fade-in">
      <div class="detail-title">详细成绩数据</div>
      <table class="score-table">
        <thead>
          <tr>
            <th>考试</th>
            <th v-for="k in subjectKeys" :key="k">{{ subjectNames[k] }}</th>
            <th>总分</th>
            <th>校排名</th>
            <th>班排名</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(label, i) in examLabels" :key="i">
            <td style="font-weight: 600; text-align: left">{{ label }}</td>
            <td v-for="k in subjectKeys" :key="k">
              {{ scores[k]?.[i] ?? "-" }}
              <span
                v-if="
                  i > 0 && scores[k]?.[i] != null && scores[k]?.[i - 1] != null
                "
                style="font-size: 11px"
              >
                <span v-if="scores[k][i] > scores[k][i - 1]" class="score-up"
                  >+{{ scores[k][i] - scores[k][i - 1] }}</span
                >
                <span
                  v-else-if="scores[k][i] < scores[k][i - 1]"
                  class="score-down"
                  >{{ scores[k][i] - scores[k][i - 1] }}</span
                >
                <span v-else class="score-flat">—</span>
              </span>
            </td>
            <td style="font-weight: 700">{{ totalScores[i] }}</td>
            <td>
              <span
                v-if="schoolRank[i]"
                :class="[
                  'rank-badge',
                  schoolRank[i] <= 50
                    ? 'rank-top'
                    : schoolRank[i] <= 100
                      ? 'rank-mid'
                      : 'rank-low',
                ]"
              >
                {{ schoolRank[i] }}
              </span>
              <span v-else>-</span>
            </td>
            <td>
              <span
                v-if="classRank[i]"
                :class="[
                  'rank-badge',
                  classRank[i] <= 10
                    ? 'rank-top'
                    : classRank[i] <= 20
                      ? 'rank-mid'
                      : 'rank-low',
                ]"
              >
                {{ classRank[i] }}
              </span>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
}
.select-wrap {
  position: relative;
}
.select-wrap select {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 12px;
  font-family: inherit;
  padding: 7px 36px 7px 14px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
  transition: all 0.2s;
}
.select-wrap select:hover {
  border-color: var(--color-primary-light);
}
.select-wrap select:focus {
  outline: none;
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 3px rgba(51, 78, 172, 0.08);
}
.select-wrap .arrow {
  pointer-events: none;
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  color: var(--color-text-light);
}
.select-wrap .arrow svg {
  width: 14px;
  height: 14px;
}

.main-chart-card {
  width: 66.666%;
  margin-bottom: 24px;
}
.main-chart-area {
  height: 360px;
}

.chart-ranking-row {
  display: flex;
  margin-bottom: 24px;
}
.chart-ranking-row .main-chart-card {
  margin-bottom: 0;
}

.ranking-section {
  padding: 0;
  border-left: none;
  display: flex;
  flex-direction: column;
}
.ranking-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 16px;
}
.ranking-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
}
.ranking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: background 0.2s;
}
.ranking-item.ranking-header {
  padding: 0 8px 8px;
  border-radius: 0;
  margin-bottom: 4px;
}
.ranking-item:hover {
  background: rgba(51, 78, 172, 0.03);
}
.ranking-item.ranking-header:hover {
  background: transparent;
}
.ranking-item.is-me {
  background: rgba(51, 78, 172, 0.06);
  border-color: rgba(51, 78, 172, 0.12);
}
.ranking-left {
  display: flex;
  align-items: center;
  gap: 0;
}
.ranking-right {
  display: flex;
  align-items: center;
  gap: 0;
  padding-left: 16px;
  border-left: 1px solid var(--color-border-light);
}
.ranking-rank {
  width: 28px;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-light);
}
.ranking-item.is-me .ranking-rank {
  color: var(--color-primary);
}
.ranking-name {
  min-width: 48px;
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ranking-item.is-me .ranking-name {
  color: var(--color-primary);
  font-weight: 700;
}
.ranking-rank-change {
  width: 48px;
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 1px;
}
.ranking-rank-change.up {
  color: var(--color-success);
}
.ranking-rank-change.down {
  color: var(--color-danger);
}
.ranking-rank-change.flat {
  color: var(--color-text-light);
}
.ranking-rank-change svg {
  width: 8px;
  height: 8px;
}
.ranking-score {
  width: 56px;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-secondary);
}
.ranking-item.is-me .ranking-score {
  color: var(--color-primary);
}
.ranking-change {
  width: 48px;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 700;
}
.ranking-change.up {
  color: var(--color-success);
}
.ranking-change.down {
  color: var(--color-danger);
}
.ranking-change.flat {
  color: var(--color-text-light);
}

.profile-section {
  flex: 1;
  padding-left: 24px;
  border-left: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.profile-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 20px;
}
.profile-info-table {
  width: 100%;
  border-collapse: collapse;
}
.profile-info-table td {
  border: 1px solid #000;
  padding: 6px 10px;
}
.profile-info-table .pil {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  width: 72px;
  white-space: nowrap;
}
.profile-info-table .piv {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}
.score-highlight {
  color: var(--color-primary);
}

.triple-columns {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  margin-bottom: 24px;
}
.content-left {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.ai-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 2px dashed var(--color-border);
  min-height: 320px;
  transition: border-color 0.3s;
}
.ai-placeholder:hover {
  border-color: var(--color-primary-light);
}
.ai-placeholder-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--color-text-light);
}
.ai-placeholder-inner svg {
  opacity: 0.4;
}
.ai-placeholder-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-secondary);
}
.ai-placeholder-sub {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-light);
  background: var(--color-bg);
  padding: 3px 12px;
  border-radius: 12px;
}

.radar-section {
  margin-bottom: 0;
}
.radar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.radar-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
}
.radar-area {
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.radar-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.radar-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
  user-select: none;
}
.radar-legend-item.hidden {
  opacity: 0.4;
  text-decoration: line-through;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.detail-section {
  margin-bottom: 0;
}
.detail-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 20px;
}
.score-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.score-table thead th {
  background: var(--color-bg);
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 12px;
  padding: 10px 14px;
  text-align: center;
  border-bottom: 2px solid var(--color-border);
  letter-spacing: 0.5px;
}
.score-table tbody td {
  padding: 12px 14px;
  text-align: center;
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text);
}
.score-table tbody tr:hover {
  background: rgba(51, 78, 172, 0.02);
}
.score-table tbody tr:last-child td {
  border-bottom: none;
}
.score-up {
  color: var(--color-success);
  font-weight: 700;
}
.score-down {
  color: var(--color-danger);
  font-weight: 700;
}
.score-flat {
  color: var(--color-text-light);
}
.rank-badge {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
}
.rank-top {
  background: rgba(51, 78, 172, 0.08);
  color: var(--color-primary);
}
.rank-mid {
  background: rgba(232, 168, 56, 0.08);
  color: var(--color-warning);
}
.rank-low {
  background: rgba(239, 68, 68, 0.06);
  color: var(--color-danger);
}

.fade-in {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeIn 0.5s ease forwards;
}
.fade-in:nth-child(1) {
  animation-delay: 0.05s;
}
.fade-in:nth-child(2) {
  animation-delay: 0.12s;
}
.fade-in:nth-child(3) {
  animation-delay: 0.19s;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .scores-page {
    padding: 24px 24px 60px;
  }
  .triple-columns {
    grid-template-columns: 1fr;
    width: 100%;
  }
  .content-left {
    grid-template-columns: 1fr;
  }
  .ai-placeholder {
    min-height: 200px;
  }
  .chart-ranking-row {
    flex-direction: column;
  }
  .main-chart-card {
    width: 100%;
  }
  .profile-section {
    padding-left: 0;
    border-left: none;
    border-top: 1px solid var(--color-border-light);
    padding-top: 16px;
  }
}
</style>


