<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { getMyHomework, submitHomework } from "../../api/homework";
import { EditPen, View, Calendar, User, Trophy } from "@element-plus/icons-vue";

interface HomeworkItem {
  id: number;
  title: string;
  description: string;
  subject: string;
  class_id: number;
  class_name: string;
  teacher_id: number;
  teacher_name: string;
  due_date: string;
  created_at: string;
  status: "unsubmitted" | "submitted" | "graded";
  grade: number | null;
  feedback: string | null;
  submission_id: number | null;
  submission_content: string | null;
  submitted_at: string | null;
}

const homeworkList = ref<HomeworkItem[]>([]);
const loading = ref(true);
const activeFilter = ref<"all" | "unsubmitted" | "submitted" | "graded">("all");

// Dialog / Drawer control
const detailsVisible = ref(false);
const selectedHw = ref<HomeworkItem | null>(null);
const submitContent = ref("");
const submitLoading = ref(false);

const SUBJECT_NAMES: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const SUBJECT_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  chinese: { bg: "#EFF6FF", border: "#BAD6EB", text: "#334EAC" },
  math: { bg: "#ECFDF5", border: "#A7F3D0", text: "#047857" },
  english: { bg: "#FFFBEB", border: "#FDE68A", text: "#B45309" },
  science: { bg: "#F5F3FF", border: "#DDD6FE", text: "#6D28D9" },
  ethics: { bg: "#FDF2F8", border: "#FBCFE8", text: "#BE185D" },
};

function getSubjectStyle(subject: string) {
  return SUBJECT_COLORS[subject] || { bg: "#EDF1F6", border: "#BAD6EB", text: "#1F2937" };
}

const stats = computed(() => {
  const total = homeworkList.value.length;
  const unsubmitted = homeworkList.value.filter((h) => h.status === "unsubmitted").length;
  const submitted = homeworkList.value.filter((h) => h.status === "submitted").length;
  const graded = homeworkList.value.filter((h) => h.status === "graded").length;
  
  const gradedScores = homeworkList.value.filter((h) => h.status === "graded" && h.grade !== null);
  const avgGrade = gradedScores.length 
    ? (gradedScores.reduce((acc, curr) => acc + (curr.grade || 0), 0) / gradedScores.length).toFixed(1)
    : "-";

  return { total, unsubmitted, submitted, graded, avgGrade };
});

const filteredHomework = computed(() => {
  if (activeFilter.value === "all") return homeworkList.value;
  return homeworkList.value.filter((h) => h.status === activeFilter.value);
});

async function loadHomework() {
  loading.value = true;
  try {
    const res: any = await getMyHomework();
    homeworkList.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取作业列表失败");
  } finally {
    loading.value = false;
  }
}

function openDetails(hw: HomeworkItem) {
  selectedHw.value = hw;
  submitContent.value = hw.submission_content || "";
  detailsVisible.value = true;
}

async function handleHomeworkSubmit() {
  if (!selectedHw.value) return;
  if (!submitContent.value.trim()) {
    ElMessage.warning("请输入作业内容");
    return;
  }

  submitLoading.value = true;
  try {
    await submitHomework(selectedHw.value.id, submitContent.value);
    ElMessage.success("作业提交成功");
    detailsVisible.value = false;
    loadHomework();
  } catch (error) {
    console.error(error);
    ElMessage.error("提交作业失败");
  } finally {
    submitLoading.value = false;
  }
}

function formatTime(timeStr: string) {
  if (!timeStr) return "";
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

function isOverdue(dueStr: string) {
  return new Date(dueStr) < new Date();
}

onMounted(() => {
  loadHomework();
});
</script>

<template>
  <div class="homework-container" v-loading="loading">
    <!-- 顶部看板 -->
    <div class="stats-overview">
      <div class="stat-card total">
        <div class="stat-icon"><Calendar /></div>
        <div class="stat-info">
          <span class="stat-label">总布置</span>
          <span class="stat-value">{{ stats.total }}</span>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon"><EditPen /></div>
        <div class="stat-info">
          <span class="stat-label">未提交</span>
          <span class="stat-value">{{ stats.unsubmitted }}</span>
        </div>
      </div>
      <div class="stat-card submitted">
        <div class="stat-icon"><View /></div>
        <div class="stat-info">
          <span class="stat-label">待批改</span>
          <span class="stat-value">{{ stats.submitted }}</span>
        </div>
      </div>
      <div class="stat-card graded">
        <div class="stat-icon"><Trophy /></div>
        <div class="stat-info">
          <span class="stat-label">平均分</span>
          <span class="stat-value">{{ stats.avgGrade }}</span>
        </div>
      </div>
    </div>

    <!-- 过滤器控制栏 -->
    <div class="filter-bar">
      <div class="custom-tabs">
        <button 
          v-for="tab in [
            { key: 'all', label: '全部作业' },
            { key: 'unsubmitted', label: '未提交' },
            { key: 'submitted', label: '已提交' },
            { key: 'graded', label: '已批改' }
          ]" 
          :key="tab.key"
          :class="['tab-item', { active: activeFilter === tab.key }]"
          @click="activeFilter = tab.key as any"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 作业列表 -->
    <div v-if="filteredHomework.length === 0" class="empty-state">
      <el-empty description="当前暂无相关作业" />
    </div>

    <div v-else class="homework-grid">
      <div 
        v-for="hw in filteredHomework" 
        :key="hw.id"
        class="hw-card"
        @click="openDetails(hw)"
      >
        <div class="hw-card-header">
          <span 
            class="subject-tag"
            :style="{
              backgroundColor: getSubjectStyle(hw.subject).bg,
              border: `1px solid ${getSubjectStyle(hw.subject).border}`,
              color: getSubjectStyle(hw.subject).text
            }"
          >
            {{ SUBJECT_NAMES[hw.subject] || hw.subject }}
          </span>
          
          <span :class="['status-badge', hw.status]">
            {{ 
              hw.status === "unsubmitted" 
                ? (isOverdue(hw.due_date) ? "已逾期" : "未提交") 
                : (hw.status === "submitted" ? "已提交" : `得分 ${hw.grade}`)
            }}
          </span>
        </div>

        <h3 class="hw-title">{{ hw.title }}</h3>
        
        <p class="hw-desc">{{ hw.description || "没有提供详细说明。" }}</p>

        <div class="hw-card-footer">
          <div class="meta-item text-secondary">
            <el-icon><User /></el-icon>
            <span>{{ hw.teacher_name }} 老师</span>
          </div>
          <div :class="['meta-item', { overdue: isOverdue(hw.due_date) && hw.status === 'unsubmitted' }]">
            <el-icon><Calendar /></el-icon>
            <span>截止: {{ formatTime(hw.due_date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 作业详情 & 提交模态框 -->
    <el-dialog
      v-model="detailsVisible"
      :title="selectedHw ? `${SUBJECT_NAMES[selectedHw.subject] || ''}作业详情` : '作业详情'"
      width="680px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <div v-if="selectedHw" class="hw-dialog-content">
        <!-- 基础信息 -->
        <div class="hw-details-header">
          <h2>{{ selectedHw.title }}</h2>
          <div class="hw-meta-grid">
            <div class="meta-block">
              <span class="label">发布老师：</span>
              <span class="value">{{ selectedHw.teacher_name }}</span>
            </div>
            <div class="meta-block">
              <span class="label">截止时间：</span>
              <span class="value" :class="{ danger: isOverdue(selectedHw.due_date) && selectedHw.status === 'unsubmitted' }">
                {{ formatTime(selectedHw.due_date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 题目描述 -->
        <div class="hw-section">
          <h3 class="section-title">作业要求</h3>
          <div class="section-box description-box">
            {{ selectedHw.description || "无详细作业描述。" }}
          </div>
        </div>

        <!-- 学生作业提交区/展示区 -->
        <div class="hw-section">
          <h3 class="section-title">我的提交</h3>
          
          <!-- 编辑区 (未提交 或 可重新提交) -->
          <div v-if="selectedHw.status === 'unsubmitted' || selectedHw.status === 'submitted'" class="submission-edit">
            <el-input
              v-model="submitContent"
              type="textarea"
              :rows="6"
              placeholder="请输入你的作业解答或学习反馈..."
              maxlength="1000"
              show-word-limit
            />
            <div class="edit-footer">
              <span class="hint" v-if="selectedHw.status === 'submitted'">重新提交将覆盖已提交的内容</span>
              <span class="hint" v-else>注意截止时间，请在截止前提交</span>
              <el-button 
                type="primary" 
                :loading="submitLoading"
                @click="handleHomeworkSubmit"
              >
                {{ selectedHw.status === 'submitted' ? '重新提交' : '提交作业' }}
              </el-button>
            </div>
          </div>

          <!-- 只读展示区 (已批改) -->
          <div v-else class="section-box submission-box">
            {{ selectedHw.submission_content }}
            <div class="submitted-time">提交时间: {{ formatTime(selectedHw.submitted_at || "") }}</div>
          </div>
        </div>

        <!-- 批改结果区 -->
        <div v-if="selectedHw.status === 'graded'" class="hw-section feedback-section">
          <h3 class="section-title">批改结果</h3>
          <div class="feedback-grid">
            <div class="score-display">
              <div class="score-circle">
                <span class="score-val">{{ selectedHw.grade }}</span>
                <span class="score-lbl">得分</span>
              </div>
            </div>
            <div class="feedback-box">
              <div class="teacher-title">{{ selectedHw.teacher_name }} 老师评语:</div>
              <div class="feedback-text">{{ selectedHw.feedback || "好！" }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.homework-container {
  width: 100%;
}

/* --- 顶部看板 --- */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 20px 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(8,31,92,0.04), 0 0 0 1px rgba(8,31,92,0.02);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}
.stat-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3.5px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: 0 0 4px 4px;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(8,31,92,0.1), 0 0 0 1px rgba(51,78,172,0.08);
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(51,78,172,0.1), rgba(51,78,172,0.04));
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23px;
  transition: transform 0.3s;
  box-shadow: 0 4px 12px rgba(51,78,172,0.08);
}
.stat-card:hover .stat-icon { transform: scale(1.1) rotate(-3deg); }
.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, rgba(232,168,56,0.12), rgba(245,158,11,0.04));
  color: var(--color-warning);
  box-shadow: 0 4px 12px rgba(232,168,56,0.1);
}
.stat-card.pending::before {
  background: linear-gradient(90deg, #E8A838, #F59E0B, #FBBF24);
}
.stat-card.submitted .stat-icon {
  background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(52,211,153,0.04));
  color: var(--color-success);
  box-shadow: 0 4px 12px rgba(16,185,129,0.1);
}
.stat-card.submitted::before {
  background: linear-gradient(90deg, #10B981, #34D399, #6EE7B7);
}
.stat-card.graded .stat-icon {
  background: linear-gradient(135deg, rgba(110,86,219,0.12), rgba(167,139,250,0.04));
  color: #6e56db;
  box-shadow: 0 4px 12px rgba(110,86,219,0.1);
}
.stat-card.graded::before {
  background: linear-gradient(90deg, #6e56db, #a78bfa, #c4b5fd);
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}
.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

/* --- 过滤器控制栏 --- */
.filter-bar {
  margin-bottom: 28px;
}
.custom-tabs {
  display: inline-flex;
  background: linear-gradient(135deg, #F3F4F6, #E5E7EB);
  padding: 4px;
  border-radius: 14px;
  gap: 4px;
}
.tab-item {
  background: transparent;
  border: none;
  padding: 9px 22px;
  border-radius: 11px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.tab-item:hover {
  color: var(--color-primary);
  background: rgba(255,255,255,0.5);
}
.tab-item.active {
  background: #FFFFFF;
  color: var(--color-primary);
  box-shadow: 0 2px 10px rgba(51,78,172,0.12), 0 0 0 1px rgba(51,78,172,0.06);
}

/* --- 作业列表 Grid --- */
.homework-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
}
.hw-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 22px 22px 22px 28px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(8,31,92,0.04);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.hw-card::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  border-radius: 5px 0 0 5px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  opacity: 0.7;
  transition: opacity 0.3s, width 0.3s;
}
.hw-card:hover::after { opacity: 1; width: 6px; }
.hw-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(8,31,92,0.1), 0 0 0 1px rgba(51,78,172,0.06);
  border-color: var(--color-primary-light);
}
.hw-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.subject-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
  letter-spacing: 0.5px;
}
.status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
}
.status-badge.unsubmitted {
  background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(248,113,113,0.06));
  color: var(--color-danger);
}
.status-badge.submitted {
  background: linear-gradient(135deg, rgba(232,168,56,0.1), rgba(251,191,36,0.06));
  color: var(--color-warning);
}
.status-badge.graded {
  background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(52,211,153,0.06));
  color: var(--color-success);
}
.hw-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 10px;
  line-height: 1.4;
}
.hw-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 41px;
}
.hw-card-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-light);
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  padding-top: 14px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.meta-item.overdue {
  color: var(--color-danger);
  font-weight: 600;
}

.empty-state {
  padding: 60px 0;
  background: var(--color-bg-card);
  border-radius: 16px;
  border: 1px solid var(--color-border-light);
}

/* --- 详情对话框 --- */
.custom-dialog :deep(.el-dialog) {
  border-radius: 18px;
  background: var(--color-bg-content);
  box-shadow: 0 24px 80px rgba(8,31,92,0.14), 0 0 0 1px rgba(8,31,92,0.04);
}
.custom-dialog :deep(.el-dialog__header) {
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border-light);
}
.custom-dialog :deep(.el-dialog__body) {
  padding: 28px;
}
.hw-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.hw-details-header h2 {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-primary);
  margin-bottom: 12px;
}
.hw-meta-grid {
  display: flex;
  gap: 32px;
  font-size: 13px;
}
.meta-block .label {
  color: var(--color-text-secondary);
}
.meta-block .value {
  color: var(--color-text);
  font-weight: 600;
}
.meta-block .value.danger {
  color: var(--color-danger);
}
.hw-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  position: relative;
  padding-left: 12px;
}
.section-title::before {
  content: "";
  position: absolute;
  left: 0;
  top: 2px;
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  border-radius: 3px;
}
.section-box {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 18px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
}
.description-box {
  background: linear-gradient(135deg, rgba(255,249,240,0.6), rgba(255,251,235,0.4));
}
.submission-box {
  background: #ffffff;
  position: relative;
}
.submitted-time {
  margin-top: 12px;
  font-size: 11px;
  color: var(--color-text-light);
  text-align: right;
}
.submission-edit {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.submission-edit :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: var(--color-border);
}
.submission-edit :deep(.el-textarea__inner:focus) {
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(51, 78, 172, 0.08);
}
.edit-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.edit-footer .hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 批改结果反馈 */
.feedback-section {
  border-top: 1px dashed var(--color-border);
  padding-top: 22px;
}
.feedback-grid {
  display: flex;
  gap: 22px;
  align-items: stretch;
}
.score-display {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.score-circle {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  border: 3px double var(--color-success);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-success);
  background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(52,211,153,0.03));
  box-shadow: 0 6px 24px rgba(16,185,129,0.15), inset 0 2px 8px rgba(16,185,129,0.06);
}
.score-val {
  font-size: 28px;
  font-weight: 900;
  line-height: 1;
}
.score-lbl {
  font-size: 10px;
  font-weight: 700;
  margin-top: 3px;
}
.feedback-box {
  flex: 1;
  background: linear-gradient(135deg, rgba(16,185,129,0.04), rgba(52,211,153,0.02));
  border: 1px solid rgba(16, 185, 129, 0.12);
  border-radius: 12px;
  padding: 18px 20px;
}
.teacher-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 6px;
}
.feedback-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

/* 入场动画 */
.hw-card {
  animation: cardFadeIn 0.4s ease both;
}
.hw-card:nth-child(2) { animation-delay: 0.06s; }
.hw-card:nth-child(3) { animation-delay: 0.12s; }
.hw-card:nth-child(4) { animation-delay: 0.18s; }
.hw-card:nth-child(5) { animation-delay: 0.24s; }
.hw-card:nth-child(6) { animation-delay: 0.3s; }
@keyframes cardFadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-card {
  animation: statPop 0.4s ease both;
}
.stat-card:nth-child(2) { animation-delay: 0.05s; }
.stat-card:nth-child(3) { animation-delay: 0.1s; }
.stat-card:nth-child(4) { animation-delay: 0.15s; }
@keyframes statPop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  .homework-grid {
    grid-template-columns: 1fr;
  }
}
</style>
