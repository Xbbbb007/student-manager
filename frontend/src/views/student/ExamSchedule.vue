<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { getMyExamSchedules, submitTest } from "../../api/exam_schedule";
import { Calendar, Location, Checked, Timer, Edit } from "@element-plus/icons-vue";

interface ExamScheduleItem {
  id: number;
  name: string;
  class_id: number;
  class_name: string;
  subject: string;
  subject_name: string;
  exam_date: string;
  start_time: string;
  end_time: string;
  location: string;
  status: "未开始" | "进行中" | "已结束";
  score: number | null;
  answers: string | null;
  submission_status: "unsubmitted" | "submitted" | "graded";
}

const schedules = ref<ExamScheduleItem[]>([]);
const loading = ref(true);

const showSubmitDialog = ref(false);
const activeTest = ref<ExamScheduleItem | null>(null);
const submitContent = ref("");
const submitLoading = ref(false);

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
  const upcoming = schedules.value.filter((s) => s.status === "未开始").length;
  const active = schedules.value.filter((s) => s.status === "进行中").length;
  const completed = schedules.value.filter((s) => s.status === "已结束").length;
  return { upcoming, active, completed };
});

async function loadSchedules() {
  loading.value = true;
  try {
    const res: any = await getMyExamSchedules();
    schedules.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取测试列表失败");
  } finally {
    loading.value = false;
  }
}

function openSubmitTest(item: ExamScheduleItem) {
  activeTest.value = item;
  submitContent.value = item.answers || "";
  showSubmitDialog.value = true;
}

async function handleTestSubmit() {
  if (!activeTest.value) return;
  if (!submitContent.value.trim()) {
    ElMessage.warning("请填写测试答案内容");
    return;
  }

  submitLoading.value = true;
  try {
    await submitTest(activeTest.value.id, submitContent.value);
    ElMessage.success("测试提交成功！");
    showSubmitDialog.value = false;
    loadSchedules();
  } catch (error) {
    console.error(error);
    ElMessage.error("测试提交失败");
  } finally {
    submitLoading.value = false;
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

onMounted(() => {
  loadSchedules();
});
</script>

<template>
  <div class="exam-schedule-container" v-loading="loading">
    <!-- 顶部数据看板 -->
    <div class="exam-stats">
      <div class="estat-card upcoming">
        <div class="estat-icon"><Calendar /></div>
        <div class="estat-info">
          <span class="estat-label">近期测试</span>
          <span class="estat-value">{{ stats.upcoming }} <small>场</small></span>
        </div>
      </div>
      <div class="estat-card active">
        <div class="estat-icon"><Timer /></div>
        <div class="estat-info">
          <span class="estat-label">进行中测试</span>
          <span class="estat-value pulsing">{{ stats.active }} <small>场</small></span>
        </div>
      </div>
      <div class="estat-card completed">
        <div class="estat-icon"><Checked /></div>
        <div class="estat-info">
          <span class="estat-label">已考测试</span>
          <span class="estat-value">{{ stats.completed }} <small>场</small></span>
        </div>
      </div>
    </div>

    <!-- 时间轴 -->
    <div v-if="schedules.length === 0" class="empty-state">
      <el-empty description="当前暂无课堂测试" />
    </div>

    <div v-else class="timeline-wrapper">
      <div class="custom-timeline">
        <div 
          v-for="s in schedules" 
          :key="s.id"
          :class="['timeline-item', s.status]"
        >
          <!-- 时间轴小圆点和线 -->
          <div class="timeline-line-indicator">
            <div class="node-dot"></div>
          </div>

          <!-- 测试卡片内容 -->
          <div class="timeline-content-card">
            <div class="card-header">
              <div class="header-left">
                <span 
                  class="subject-tag"
                  :style="{
                    backgroundColor: getSubjectStyle(s.subject).bg,
                    border: `1px solid ${getSubjectStyle(s.subject).border}`,
                    color: getSubjectStyle(s.subject).text
                  }"
                >
                  {{ s.subject_name }}
                </span>
                <span class="exam-date-title">{{ formatDate(s.exam_date) }}</span>
              </div>
              <span :class="['status-badge', s.status]">{{ s.status }}</span>
            </div>

            <h3 class="exam-name">{{ s.name }}</h3>

            <div class="exam-meta-details">
              <div class="meta-row">
                <el-icon><Timer /></el-icon>
                <span>时间：{{ s.start_time }} - {{ s.end_time }}</span>
              </div>
              <div class="meta-row">
                <el-icon><Location /></el-icon>
                <span>测试形式：{{ s.location }}</span>
              </div>
            </div>

            <!-- 学生作答得分展示区 -->
            <div class="card-status-info" v-if="s.status === '已结束'">
              <div class="graded-score-box" v-if="s.submission_status === 'graded'">
                <span class="lbl">测试得分：</span>
                <strong class="val">{{ s.score }} 分</strong>
              </div>
              <span class="pending-lbl" v-else-if="s.submission_status === 'submitted'">答案已提交，等待评分</span>
              <span class="missing-lbl" v-else>缺考（未提交作答）</span>
            </div>

            <!-- 操作 -->
            <div class="card-actions">
              <el-button 
                v-if="s.status === '进行中'"
                type="warning" 
                size="small"
                :icon="Edit"
                @click="openSubmitTest(s)"
              >
                {{ s.submission_status === 'unsubmitted' ? '开始测试' : '修改作答' }}
              </el-button>
              
              <el-button
                v-if="s.status === '已结束' && s.submission_status !== 'unsubmitted'"
                type="info"
                size="small"
                plain
                @click="openSubmitTest(s)"
              >
                查看作答
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 开始测试 / 查看测试作答 Dialog -->
    <el-dialog
      v-model="showSubmitDialog"
      :title="activeTest ? `${activeTest.name} - 在线答题` : '在线答题'"
      width="580px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <div v-if="activeTest" class="test-dialog-body">
        <div class="test-instruction">
          <p><strong>测试科目：</strong>{{ activeTest.subject_name }}</p>
          <p><strong>注意事项：</strong>请在空白框中录入您的答题答案。确认无误后点击提交。</p>
        </div>

        <div class="answers-area">
          <div class="lbl">您的作答内容：</div>
          <el-input 
            v-model="submitContent" 
            type="textarea" 
            :rows="8" 
            placeholder="请在此输入作答文字..." 
            :disabled="activeTest.status === '已结束'"
          />
        </div>

        <!-- 成绩报告（如果是已出分状态） -->
        <div class="score-report" v-if="activeTest.status === '已结束' && activeTest.submission_status === 'graded'">
          <div class="score-circle">
            <span class="num">{{ activeTest.score }}</span>
            <span class="unit">得分</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer" v-if="activeTest && activeTest.status !== '已结束'">
          <el-button @click="showSubmitDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleTestSubmit">确认提交</el-button>
        </div>
        <div class="dialog-footer" v-else>
          <el-button type="primary" @click="showSubmitDialog = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.exam-schedule-container {
  width: 100%;
}

/* === 看板 === */
.exam-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}
.estat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: 0 2px 8px rgba(8,31,92,0.04), 0 0 0 1px rgba(8,31,92,0.02);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: statPop 0.4s ease both;
}
.estat-card:nth-child(2) { animation-delay: 0.06s; }
.estat-card:nth-child(3) { animation-delay: 0.12s; }
@keyframes statPop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.estat-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3.5px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: 0 0 4px 4px;
}
.estat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(8,31,92,0.1), 0 0 0 1px rgba(51,78,172,0.08);
}
.estat-icon {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(51,78,172,0.1), rgba(51,78,172,0.04));
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: transform 0.3s;
  box-shadow: 0 4px 12px rgba(51,78,172,0.08);
}
.estat-card:hover .estat-icon { transform: scale(1.1) rotate(-3deg); }
.estat-card.upcoming::before {
  background: linear-gradient(90deg, var(--color-primary), #6B8DD6, #93B4F5);
}
.estat-card.active .estat-icon {
  background: linear-gradient(135deg, rgba(232,168,56,0.12), rgba(245,158,11,0.04));
  color: var(--color-warning);
  box-shadow: 0 4px 12px rgba(232,168,56,0.1);
}
.estat-card.active::before {
  background: linear-gradient(90deg, var(--color-warning), #F59E0B, #FBBF24);
}
.estat-card.completed .estat-icon {
  background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(52,211,153,0.04));
  color: var(--color-success);
  box-shadow: 0 4px 12px rgba(16,185,129,0.1);
}
.estat-card.completed::before {
  background: linear-gradient(90deg, var(--color-success), #34D399, #6EE7B7);
}
.estat-info {
  display: flex;
  flex-direction: column;
}
.estat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}
.estat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
}
.estat-value small {
  font-size: 12px;
  font-weight: normal;
  color: var(--color-text-secondary);
}

/* Pulsing */
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.06); opacity: 0.75; }
  100% { transform: scale(1); opacity: 1; }
}
.pulsing {
  color: var(--color-warning);
  animation: pulse 2s infinite ease-in-out;
}

/* === 时间轴 === */
.timeline-wrapper {
  padding: 10px 0;
}
.custom-timeline {
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 20px;
}
.custom-timeline::before {
  content: "";
  position: absolute;
  left: 29px;
  top: 10px;
  bottom: 10px;
  width: 3px;
  background: linear-gradient(180deg, rgba(51,78,172,0.2), rgba(16,185,129,0.25), rgba(232,168,56,0.15));
  border-radius: 3px;
}

.timeline-item {
  display: flex;
  margin-bottom: 28px;
  position: relative;
  animation: timelineSlideIn 0.45s ease both;
}
.timeline-item:nth-child(2) { animation-delay: 0.08s; }
.timeline-item:nth-child(3) { animation-delay: 0.16s; }
.timeline-item:nth-child(4) { animation-delay: 0.24s; }
.timeline-item:nth-child(5) { animation-delay: 0.32s; }
.timeline-item:last-child { margin-bottom: 0; }

@keyframes timelineSlideIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}

.timeline-line-indicator {
  width: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  margin-right: 15px;
  position: relative;
  z-index: 2;
  margin-top: 22px;
}

.node-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--color-border);
  border: 3px solid #ffffff;
  transition: all 0.3s;
  box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
}

.timeline-item.未开始 .node-dot {
  background: linear-gradient(135deg, var(--color-primary), #6B8DD6);
  box-shadow: 0 0 0 4px rgba(51,78,172,0.15), 0 2px 8px rgba(51,78,172,0.2);
}
.timeline-item.进行中 .node-dot {
  background: linear-gradient(135deg, var(--color-warning), #FBBF24);
  box-shadow: 0 0 0 5px rgba(232,168,56,0.18), 0 0 16px rgba(232,168,56,0.3);
  animation: pulseGlow 2s infinite ease-in-out;
}
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 0 5px rgba(232,168,56,0.18), 0 0 16px rgba(232,168,56,0.3); }
  50% { box-shadow: 0 0 0 8px rgba(232,168,56,0.1), 0 0 24px rgba(232,168,56,0.2); }
}
.timeline-item.已结束 .node-dot {
  background: linear-gradient(135deg, var(--color-success), #34D399);
  box-shadow: 0 0 0 4px rgba(16,185,129,0.15), 0 2px 8px rgba(16,185,129,0.2);
}

/* === 卡片内容 === */
.timeline-content-card {
  flex: 1;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 22px 28px;
  box-shadow: 0 3px 12px rgba(8,31,92,0.04);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}
.timeline-content-card::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  border-radius: 5px 0 0 5px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  opacity: 0.6;
  transition: opacity 0.3s, width 0.3s;
}
.timeline-content-card:hover::after { opacity: 1; width: 6px; }
.timeline-content-card:hover {
  transform: translateX(8px);
  box-shadow: 0 14px 36px rgba(8,31,92,0.1);
  border-color: var(--color-primary-light);
}

.timeline-item.进行中 .timeline-content-card::after {
  background: linear-gradient(180deg, var(--color-warning), #FBBF24);
}
.timeline-item.已结束 .timeline-content-card::after {
  background: linear-gradient(180deg, var(--color-success), #34D399);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.card-header .status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
}
.status-badge.未开始 {
  background: linear-gradient(135deg, rgba(51,78,172,0.1), rgba(107,141,214,0.06));
  color: var(--color-primary);
}
.status-badge.进行中 {
  background: linear-gradient(135deg, rgba(232,168,56,0.12), rgba(251,191,36,0.06));
  color: var(--color-warning);
}
.status-badge.el-dialog {
  z-index: 20000 !important;
}
.status-badge.已结束 {
  background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(52,211,153,0.06));
  color: var(--color-success);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.subject-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
  letter-spacing: 0.5px;
}
.exam-date-title {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.exam-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 14px;
}

.exam-meta-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  border-bottom: 1px dashed rgba(0, 0, 0, 0.05);
  padding-bottom: 16px;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* === 得分结果 === */
.card-status-info {
  margin-top: 16px;
  font-size: 13px;
}
.graded-score-box {
  display: flex;
  align-items: center;
  gap: 8px;
}
.graded-score-box .lbl {
  color: var(--color-text-secondary);
  font-weight: 500;
}
.graded-score-box .val {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-success), #34D399, #6EE7B7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.pending-lbl {
  color: var(--color-warning);
  font-weight: 600;
}
.missing-lbl {
  color: var(--color-text-light);
}

.card-actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  padding: 60px 0;
  background: var(--color-bg-card);
  border-radius: 16px;
  border: 1px solid var(--color-border-light);
}

/* === Dialog === */
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
.test-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.test-instruction {
  background: linear-gradient(135deg, rgba(8,31,92,0.025), rgba(51,78,172,0.015));
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px 18px;
  font-size: 13px;
  color: var(--color-text);
  line-height: 1.7;
}
.answers-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.answers-area .lbl {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
  position: relative;
  padding-left: 12px;
}
.answers-area .lbl::before {
  content: "";
  position: absolute;
  left: 0;
  top: 3px;
  width: 4px;
  height: 14px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  border-radius: 3px;
}
.answers-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: var(--color-border);
}
.answers-area :deep(.el-textarea__inner:focus) {
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(51, 78, 172, 0.08);
}
.score-report {
  margin-top: 14px;
  display: flex;
  justify-content: center;
}
.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px double var(--color-success);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(52,211,153,0.03));
  color: var(--color-success);
  box-shadow: 0 8px 28px rgba(16,185,129,0.15), inset 0 2px 8px rgba(16,185,129,0.06);
}
.score-circle .num {
  font-size: 30px;
  font-weight: 900;
  line-height: 1;
}
.score-circle .unit {
  font-size: 11px;
  margin-top: 3px;
  font-weight: 700;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .exam-stats { grid-template-columns: 1fr; }
}
</style>
