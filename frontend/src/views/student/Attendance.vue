<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getMyAttendanceLogs, getMyAttendanceStats, getMyLeaves, createMyLeaveRequest } from "../../api/attendance";
import { Calendar, Timer, Checked, Warning, UserFilled, DocumentAdd, RefreshLeft } from "@element-plus/icons-vue";

interface AttendanceLog {
  id: number;
  date: string;
  period: number;
  status: string;
  reason: string | null;
}

interface LeaveRecord {
  id: number;
  start_date: string;
  end_date: string;
  reason: string;
  status: string;
  approved_by_name: string | null;
  feedback: string | null;
}

const stats = ref({
  total: 0,
  present: 0,
  tardy: 0,
  absent: 0,
  leave: 0,
  attendance_rate: 100.0,
});

const logs = ref<AttendanceLog[]>([]);
const leaves = ref<LeaveRecord[]>([]);
const loading = ref(true);

const showAddLeaveDialog = ref(false);
const submitLoading = ref(false);
const form = ref({
  dateRange: [] as any[],
  reason: "",
});

const STATUS_MAP: Record<string, { text: string; type: string; color: string }> = {
  present: { text: "出勤", type: "success", color: "#10B981" },
  tardy: { text: "迟到", type: "warning", color: "#F59E0B" },
  absent: { text: "缺勤", type: "danger", color: "#EF4444" },
  leave: { text: "请假", type: "info", color: "#334EAC" },
};

const LEAVE_STATUS_MAP: Record<string, { text: string; type: string }> = {
  pending: { text: "审核中", type: "warning" },
  approved: { text: "已批准", type: "success" },
  rejected: { text: "已拒绝", type: "danger" },
};

async function loadData() {
  loading.value = true;
  try {
    const [statsRes, logsRes, leavesRes]: any = await Promise.all([
      getMyAttendanceStats(),
      getMyAttendanceLogs(),
      getMyLeaves(),
    ]);
    stats.value = statsRes.data;
    logs.value = logsRes.data || [];
    leaves.value = leavesRes.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取考勤请假数据失败");
  } finally {
    loading.value = false;
  }
}

async function handleSubmitLeave() {
  if (!form.value.dateRange || form.value.dateRange.length < 2) {
    ElMessage.warning("请选择请假日期区间");
    return;
  }
  if (!form.value.reason.trim()) {
    ElMessage.warning("请输入请假原因");
    return;
  }

  submitLoading.value = true;
  try {
    const d1 = new Date(form.value.dateRange[0]);
    const d2 = new Date(form.value.dateRange[1]);
    const start_date = `${d1.getFullYear()}-${String(d1.getMonth() + 1).padStart(2, "0")}-${String(d1.getDate()).padStart(2, "0")}`;
    const end_date = `${d2.getFullYear()}-${String(d2.getMonth() + 1).padStart(2, "0")}-${String(d2.getDate()).padStart(2, "0")}`;

    await createMyLeaveRequest({
      start_date,
      end_date,
      reason: form.value.reason,
    });
    ElMessage.success("请假申请已提交，等待审核");
    showAddLeaveDialog.value = false;
    form.value = {
      dateRange: [],
      reason: "",
    };
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("提交请假申请失败");
  } finally {
    submitLoading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="attendance-container" v-loading="loading">
    <!-- 统计看板 -->
    <div class="stats-overview">
      <div class="stat-card rate-card">
        <div class="stat-icon rate-icon"><Checked /></div>
        <div class="stat-info">
          <span class="lbl">出勤率</span>
          <span class="val">{{ stats.attendance_rate }}%</span>
        </div>
      </div>
      <div class="stat-card present-card">
        <div class="stat-info">
          <span class="lbl">正常出勤</span>
          <span class="val">{{ stats.present }} <small>节</small></span>
        </div>
      </div>
      <div class="stat-card tardy-card">
        <div class="stat-info">
          <span class="lbl">迟到次数</span>
          <span class="val text-warning">{{ stats.tardy }} <small>次</small></span>
        </div>
      </div>
      <div class="stat-card absent-card">
        <div class="stat-info">
          <span class="lbl">缺勤次数</span>
          <span class="val text-danger">{{ stats.absent }} <small>次</small></span>
        </div>
      </div>
    </div>

    <!-- 栏目分层：考勤流水与请假记录 -->
    <div class="layout-flex">
      <!-- 考勤记录流水 -->
      <div class="flex-column logs-panel">
        <div class="section-header">
          <h3>考勤刷卡明细</h3>
          <el-button :icon="RefreshLeft" size="small" circle @click="loadData" />
        </div>

        <div class="logs-list-wrapper">
          <el-empty description="暂无考勤明细记录" v-if="logs.length === 0" />
          <div class="logs-list" v-else>
            <div v-for="log in logs" :key="log.id" class="log-item">
              <div class="log-left">
                <el-icon class="calendar-icon"><Calendar /></el-icon>
                <div class="time-meta">
                  <span class="date">{{ log.date }}</span>
                  <span class="period">第 {{ log.period }} 节课</span>
                </div>
              </div>
              <div class="log-right">
                <el-tag :type="STATUS_MAP[log.status]?.type || 'info'" size="small">
                  {{ STATUS_MAP[log.status]?.text || '未知' }}
                </el-tag>
                <span class="reason-txt" v-if="log.reason">({{ log.reason }})</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 请假记录与在线申请 -->
      <div class="flex-column leaves-panel">
        <div class="section-header">
          <h3>在线请假记录</h3>
          <el-button type="primary" :icon="DocumentAdd" size="small" @click="showAddLeaveDialog = true">
            新建请假
          </el-button>
        </div>

        <div class="leaves-list-wrapper">
          <el-empty description="暂无请假历史记录" v-if="leaves.length === 0" />
          <div class="leaves-list" v-else>
            <div v-for="lv in leaves" :key="lv.id" class="leave-card">
              <div class="lcard-header">
                <span class="date-range">{{ lv.start_date }} 至 {{ lv.end_date }}</span>
                <el-tag :type="LEAVE_STATUS_MAP[lv.status]?.type || 'info'" size="small">
                  {{ LEAVE_STATUS_MAP[lv.status]?.text || '未知' }}
                </el-tag>
              </div>
              <p class="reason"><strong>原因:</strong> {{ lv.reason }}</p>
              <div class="feedback-box" v-if="lv.approved_by_name">
                <div class="approver">
                  <el-icon><UserFilled /></el-icon>
                  <span>审批人: {{ lv.approved_by_name }}</span>
                </div>
                <p class="fb-txt" v-if="lv.feedback"><strong>评语:</strong> {{ lv.feedback }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 请假申请 Dialog -->
    <el-dialog
      v-model="showAddLeaveDialog"
      title="在线新建请假单"
      width="500px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="请假日期范围" required>
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="请假事由说明" required>
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入请假原因，如：感冒发烧需要就医等..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddLeaveDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmitLeave">提交申请</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.attendance-container {
  width: 100%;
}

/* stats */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
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
}
.rate-card {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: #ffffff;
}
.rate-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.rate-card .lbl {
  color: rgba(255, 255, 255, 0.7);
}
.rate-card .val {
  color: #ffffff;
}
.lbl {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.val {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
}
.val small {
  font-size: 11px;
  font-weight: normal;
  color: var(--color-text-secondary);
}

/* Layout */
.layout-flex {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 800px) {
  .layout-flex {
    grid-template-columns: 1fr;
  }
}

.flex-column {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 10px;
}
.section-header h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

/* log list */
.logs-list-wrapper, .leaves-list-wrapper {
  max-height: 460px;
  overflow-y: auto;
}
.logs-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.log-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(8, 31, 92, 0.01);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
}
.log-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.calendar-icon {
  font-size: 18px;
  color: var(--color-text-light);
}
.time-meta {
  display: flex;
  flex-direction: column;
}
.time-meta .date {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.time-meta .period {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.log-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.reason-txt {
  font-size: 11px;
  color: var(--color-text-light);
}

/* Leave Cards */
.leaves-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.leave-card {
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  padding: 14px;
  background: rgba(8, 31, 92, 0.015);
}
.lcard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.date-range {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text);
}
.leave-card .reason {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0 0 10px 0;
}
.feedback-box {
  background: var(--color-bg-content);
  border-radius: 6px;
  padding: 8px 12px;
  border-left: 3px solid var(--color-primary-light);
}
.approver {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 700;
  margin-bottom: 4px;
}
.fb-txt {
  font-size: 11px;
  color: var(--color-text);
  margin: 0;
}

/* Dialog */
.custom-dialog :deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
