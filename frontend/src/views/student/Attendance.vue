<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getMyAttendanceLogs,
  getMyAttendanceStats,
  getMyLeaves,
  createMyLeaveRequest,
  deleteMyLeaveRequest
} from "../../api/attendance";
import { useUserStore } from "../../stores/user";
import { Calendar, Checked, UserFilled, DocumentAdd, RefreshLeft } from "@element-plus/icons-vue";

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

const userStore = useUserStore();
const studentInfo = computed(() => userStore.userInfo);

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

// View toggle
const showMobileLeavePage = ref(false);

// Profile state (local override for double click title simulation)
const profileOverride = ref({
  id: "",
  name: ""
});

// Modals
const showProfileOverlay = ref(false);
const showAddOverlay = ref(false);

const submitLoading = ref(false);
const form = ref({
  type: "事假",
  startStr: "",
  endStr: "",
  reason: "",
});

const LEAVE_TYPES = ["事假", "病假", "回家", "公假"];

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

// Swipe status
const swipedCardId = ref<number | null>(null);
const touchStartX = ref(0);
const touchCurrentX = ref(0);
const isDragging = ref(false);

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

    // Sync profile values if override is not set
    if (!profileOverride.value.id && studentInfo.value) {
      profileOverride.value.id = studentInfo.value.username || "";
      profileOverride.value.name = studentInfo.value.name || "";
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("获取考勤请假数据失败");
  } finally {
    loading.value = false;
  }
}

function parseReason(reasonStr: string) {
  const match = reasonStr.match(/^\[(.*?)\]\s*(.*)$/);
  if (match) {
    return { type: match[1], reason: match[2] };
  }
  return { type: "事假", reason: reasonStr };
}

function formatMobileDatetime(dateStr: string) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const h = String(d.getHours()).padStart(2, '0');
  return `${y}-${m}-${day} ${h}时`;
}

function calcMobileDuration(startStr: string, endStr: string) {
  const diff = new Date(endStr).getTime() - new Date(startStr).getTime();
  if (diff <= 0) return '0天0小时';
  const totalH = Math.floor(diff / 3600000);
  return `${Math.floor(totalH / 24)}天${totalH % 24}小时`;
}

// Display state maps based on template logic
function getMobileStatus(l: LeaveRecord) {
  if (l.status === 'pending') {
    return { label: '待审批', class: 'state-pending', pending: true, active: false };
  }
  if (l.status === 'rejected') {
    return { label: '已拒绝', class: 'state-finished', pending: false, active: false };
  }
  // Approved status maps dynamically based on date
  const now = new Date().getTime();
  const start = new Date(l.start_date).getTime();
  const end = new Date(l.end_date).getTime();
  if (now < start) {
    return { label: '待休假', class: 'state-pending', pending: true, active: false };
  } else if (now >= start && now <= end) {
    return { label: '假期中', class: 'state-active', pending: false, active: true };
  } else {
    return { label: '已销假', class: 'state-finished', pending: false, active: false };
  }
}

const hasActiveOrPending = computed(() => {
  return leaves.value.some(l => {
    const statusObj = getMobileStatus(l);
    return statusObj.pending || statusObj.active;
  });
});

// Touch and drag swipe delete handlers
function handleTouchStart(e: TouchEvent | MouseEvent, _id: number) {
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
  touchStartX.value = clientX;
  touchCurrentX.value = clientX;
  isDragging.value = true;
}

function handleTouchMove(e: TouchEvent | MouseEvent, _id: number) {
  if (!isDragging.value) return;
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
  touchCurrentX.value = clientX;
  const diff = touchCurrentX.value - touchStartX.value;
  if (diff < -10) {
    swipedCardId.value = id;
  } else if (diff > 10) {
    swipedCardId.value = null;
  }
}

function handleTouchEnd() {
  isDragging.value = false;
}

async function handleDeleteLeave(id: number) {
  try {
    await ElMessageBox.confirm("确定删除/撤销此请假记录吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteMyLeaveRequest(id);
    ElMessage.success("删除成功");
    swipedCardId.value = null;
    loadData();
  } catch (error) {
    if (error !== "cancel") {
      console.error(error);
      ElMessage.error("删除失败");
    }
  }
}

// Add leave overlay action
function openAddOverlay() {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const defaultStart = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}T${pad(now.getHours())}:00`;
  const end = new Date(now.getTime() + 86400000);
  const defaultEnd = `${end.getFullYear()}-${pad(end.getMonth()+1)}-${pad(end.getDate())}T${pad(end.getHours())}:00`;

  form.value = {
    type: "事假",
    startStr: defaultStart,
    endStr: defaultEnd,
    reason: "",
  };
  showAddOverlay.value = true;
}

async function handleAddLeaveRecord() {
  if (!form.value.startStr || !form.value.endStr) {
    ElMessage.warning("请填写完整时间");
    return;
  }
  if (new Date(form.value.endStr) <= new Date(form.value.startStr)) {
    ElMessage.warning("结束时间必须晚于开始时间");
    return;
  }
  if (!form.value.reason.trim()) {
    ElMessage.warning("请填写请假原因");
    return;
  }

  submitLoading.value = true;
  try {
    await createMyLeaveRequest({
      start_date: form.value.startStr.split('T')[0],
      end_date: form.value.endStr.split('T')[0],
      reason: `[${form.value.type}] ${form.value.reason}`
    });
    ElMessage.success("请假申请已提交");
    showAddOverlay.value = false;
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("提交失败");
  } finally {
    submitLoading.value = false;
  }
}

// Double click tap helper for submit button
let lastTap = 0;
function handleSubmitBtnClick() {
  const now = Date.now();
  if (now - lastTap < 350) {
    openAddOverlay();
  } else {
    // Provide a helper tooltip on single click
    ElMessage.info("双击此按钮以新建请假单");
  }
  lastTap = now;
}

function saveProfile() {
  showProfileOverlay.value = false;
  ElMessage.success("个人信息已更新（本地模拟）");
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="attendance-container" v-loading="loading">
    
    <!-- ==================== 1. 主看板页面 ==================== -->
    <template v-if="!showMobileLeavePage">
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
            <el-button type="primary" :icon="DocumentAdd" size="small" @click="showMobileLeavePage = true">
              去请假条页面
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
    </template>

    <!-- ==================== 2. 模拟手机请假页面 ==================== -->
    <template v-else>
      <div class="mobile-layout-wrapper">
        <div class="mobile-container">
          
          <!-- Top Header -->
          <div class="m-header">
            <span class="icon" @click="showMobileLeavePage = false">✕</span>
            <span class="header-title" @dblclick="showProfileOverlay = true">日常请假</span>
            <span class="icon">⋮</span>
          </div>

          <!-- Alert Banner -->
          <div class="alert-banner" v-if="hasActiveOrPending">
            <div class="alert-icon">
              <svg class="svg-bell" viewBox="0 0 24 24">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
              </svg>
            </div>
            <div class="alert-text">
              <div id="alert-warning">当前状态不能请假或有请假未完成！</div>
              <div>同一时间段只能选择一个系统进行登记。</div>
            </div>
          </div>

          <!-- Content Area -->
          <div class="m-content">
            <div class="empty-hint" v-if="leaves.length === 0">
              <div class="icon">📋</div>
              暂无请假记录<br>双击底部按钮添加
            </div>

            <div v-else>
              <div
                v-for="l in leaves"
                :key="l.id"
                class="card-wrapper"
              >
                <!-- Swipe delete background -->
                <div class="delete-bg" @click="handleDeleteLeave(l.id)">删除</div>

                <!-- Sliding card content -->
                <div
                  class="card-slider"
                  :style="swipedCardId === l.id ? 'transform: translateX(-80px)' : 'transform: translateX(0)'"
                  @touchstart="e => handleTouchStart(e, l.id)"
                  @touchmove="e => handleTouchMove(e, l.id)"
                  @touchend="handleTouchEnd"
                  @mousedown="e => handleTouchStart(e, l.id)"
                  @mousemove="e => handleTouchMove(e, l.id)"
                  @mouseup="handleTouchEnd"
                >
                  <div :class="['card', getMobileStatus(l).class]">
                    <div class="card-row">
                      <div class="label">学号</div>
                      <div class="value flex-between">
                        <span>{{ profileOverride.id }}</span>
                        <a href="#" class="link" @click.prevent>查看详情 &gt;</a>
                      </div>
                    </div>
                    <div class="card-row">
                      <div class="label">姓名</div>
                      <div class="value">{{ profileOverride.name }}</div>
                    </div>
                    <div class="card-row">
                      <div class="label">请假时间</div>
                      <div class="value">
                        {{ formatMobileDatetime(l.start_date) }}至{{ formatMobileDatetime(l.end_date) }}
                      </div>
                    </div>
                    <div class="card-row">
                      <div class="label">请假时长</div>
                      <div class="value">
                        {{ calcMobileDuration(l.start_date, l.end_date) }}
                      </div>
                    </div>
                    <div class="card-row">
                      <div class="label">请假类型</div>
                      <div class="value">
                        {{ parseReason(l.reason).type }}
                      </div>
                    </div>
                    
                    <!-- Actions for pending leaves -->
                    <div
                      v-if="l.status === 'pending'"
                      class="card-actions"
                      style="display: flex;"
                    >
                      <button class="action-btn btn-cancel" @click="handleDeleteLeave(l.id)">撤销</button>
                      <button class="action-btn btn-finish" @click="handleDeleteLeave(l.id)">销假</button>
                    </div>

                    <!-- Stamp -->
                    <div class="stamp">{{ getMobileStatus(l).label }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom submit button (Double click to trigger add) -->
          <button class="submit-btn" @click="handleSubmitBtnClick">提交请假</button>
        </div>
      </div>
    </template>

    <!-- ==================== Overlay: 编辑个人信息 ==================== -->
    <div :class="['overlay', showProfileOverlay ? 'active' : '']" @click.self="showProfileOverlay = false">
      <div class="modal-card">
        <button class="modal-close" @click="showProfileOverlay = false">&times;</button>
        <h3>编辑个人信息</h3>
        <div class="field">
          <label>学号</label>
          <input type="text" v-model="profileOverride.id" placeholder="请输入学号">
        </div>
        <div class="field">
          <label>姓名</label>
          <input type="text" v-model="profileOverride.name" placeholder="请输入姓名">
        </div>
        <div class="modal-btns">
          <button class="btn-modal-cancel" @click="showProfileOverlay = false">取消</button>
          <button class="btn-modal-confirm" @click="saveProfile">确认</button>
        </div>
      </div>
    </div>

    <!-- ==================== Overlay: 添加请假记录 ==================== -->
    <div :class="['overlay', showAddOverlay ? 'active' : '']" @click.self="showAddOverlay = false">
      <div class="modal-card">
        <button class="modal-close" @click="showAddOverlay = false">&times;</button>
        <h3>添加请假记录</h3>
        <div class="field">
          <label>请假类型</label>
          <select v-model="form.type">
            <option v-for="t in LEAVE_TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div class="field">
          <label>开始时间</label>
          <input type="datetime-local" v-model="form.startStr">
        </div>
        <div class="field">
          <label>结束时间</label>
          <input type="datetime-local" v-model="form.endStr">
        </div>
        <div class="field">
          <label>请假原因</label>
          <input type="text" v-model="form.reason" placeholder="请输入请假事由..." style="width: 100%">
        </div>
        <div class="modal-btns">
          <button class="btn-modal-cancel" @click="showAddOverlay = false">取消</button>
          <button class="btn-modal-confirm" :disabled="submitLoading" @click="handleAddLeaveRecord">添加</button>
        </div>
      </div>
    </div>

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

/* =========================================
   Mobile View Mockup Styling
   ========================================= */
.mobile-layout-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px 0;
  background-color: var(--color-bg-content);
}

.mobile-container {
  width: 100%;
  max-width: 400px;
  height: 800px;
  background-color: #f5f6f8;
  position: relative;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
}

/* Header */
.m-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  padding: 15px;
  font-size: 18px;
  font-weight: 500;
  color: #333;
  flex-shrink: 0;
  border-bottom: 1px solid #eee;
}
.m-header .icon {
  font-size: 20px;
  cursor: pointer;
  color: #333;
  font-weight: normal;
  user-select: none;
}
.header-title {
  cursor: pointer;
  user-select: none;
  font-weight: 600;
}

/* Alert Banner */
.alert-banner {
  background-color: #fff5f7;
  color: #e04a62;
  font-size: 13px;
  padding: 10px 15px;
  line-height: 1.5;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(224, 74, 98, 0.1);
}
.alert-icon {
  flex-shrink: 0;
  margin-right: 0.8em;
  display: flex;
  align-items: center;
}
.svg-bell {
  width: 16px;
  height: 16px;
  fill: #df2d57;
}

/* Content Area */
.m-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 70px;
}

/* Swipeable Card Wrapper */
.card-wrapper {
  position: relative;
  overflow: hidden;
  margin-bottom: 12px;
}

.delete-bg {
  position: absolute;
  right: 0;
  top: 0;
  width: 80px;
  height: 100%;
  background: #ff4757;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  user-select: none;
  z-index: 1;
}

.card-slider {
  position: relative;
  z-index: 2;
  transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  touch-action: pan-y;
  will-change: transform;
}

/* Card Styles */
.card {
  background-color: #fff;
  padding: 18px 16px;
  position: relative;
  overflow: hidden;
  text-align: left;
}

.card-row {
  display: flex;
  margin-bottom: 14px;
  font-size: 14px;
}
.card-row:last-of-type {
  margin-bottom: 0;
}

.label {
  color: #333;
  width: 85px;
  flex-shrink: 0;
}
.value {
  color: rgb(114, 114, 114);
  flex: 1;
}
.value.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.link {
  color: #55c8d8;
  text-decoration: none;
  font-size: 13px;
  display: flex;
  align-items: center;
}

/* Action Buttons */
.card-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 15px;
  padding-right: 35px;
}

.action-btn {
  width: 40%;
  border: none;
  padding: 10px 0;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
}
.btn-cancel {
  background: linear-gradient(to right, #ff7a00, #ff0055);
  max-width: 140px;
}
.btn-finish {
  background: linear-gradient(to right, #40e0d0, #3bbcf6);
  max-width: 140px;
}

/* Diagonal Corner Stamp */
.stamp {
  position: absolute;
  right: -22px;
  bottom: 6px;
  width: 78px;
  text-align: center;
  color: #fff;
  font-size: 11px;
  padding: 2px 0;
  transform: rotate(-45deg);
  z-index: 5;
  font-weight: 600;
}
.state-finished { background-color: #cbd5e1; }
.state-finished .stamp { background-color: #c960ff; }
.state-pending .stamp  { background-color: #7c83ff; }
.state-active .stamp   { background-color: #63b3ed; }

/* Fixed Bottom Button */
.submit-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: #65d5e3;
  color: #fff;
  border: none;
  padding: 18px 0;
  font-size: 16px;
  font-weight: 500;
  text-align: center;
  z-index: 10;
  cursor: pointer;
}
.submit-btn:active {
  background-color: #5bbcc8;
}

/* Empty state hint */
.empty-hint {
  text-align: center;
  padding: 60px 20px;
  color: #bbb;
  font-size: 14px;
}
.empty-hint .icon {
  font-size: 40px;
  margin-bottom: 12px;
}

/* =========================================
   Overlay & Modal Cards
   ========================================= */
.overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
  align-items: center;
  justify-content: center;
}
.overlay.active {
  display: flex;
}

.modal-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px 20px 20px;
  width: 320px;
  max-width: 90vw;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  position: relative;
  text-align: left;
}

.modal-card h3 {
  font-size: 17px;
  color: #333;
  margin-bottom: 18px;
  text-align: center;
  font-weight: 600;
}

.modal-card .field {
  margin-bottom: 14px;
}
.modal-card .field label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
  font-weight: 500;
}
.modal-card .field input,
.modal-card .field select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  background: #fafafa;
  box-sizing: border-box;
}
.modal-card .field input:focus,
.modal-card .field select:focus {
  border-color: #55c8d8;
  background: #fff;
}

.modal-btns {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
.modal-btns button {
  flex: 1;
  padding: 11px 0;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.1s, opacity 0.15s;
}
.modal-btns button:active {
  transform: scale(0.97);
}
.btn-modal-cancel {
  background: #f0f0f0;
  color: #666;
}
.btn-modal-confirm {
  background: linear-gradient(135deg, #55c8d8, #3bbcf6);
  color: #fff;
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 14px;
  background: none;
  border: none;
  font-size: 20px;
  color: #bbb;
  cursor: pointer;
  line-height: 1;
}
.modal-close:hover {
  color: #888;
}
</style>
