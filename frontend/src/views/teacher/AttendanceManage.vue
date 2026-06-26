<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getTeacherClassLogs, takeRollCall, getTeacherLeaves, approveLeaveRequest } from "../../api/attendance";
import { getTeacherClasses } from "../../api/scores";
import { Checked } from "@element-plus/icons-vue";

interface ClassItem {
  id: number;
  name: string;
}

interface StudentItem {
  id: number;
  name: string;
  username: string;
  status: string;
  reason?: string;
}

interface LeaveRecord {
  id: number;
  student_name: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: string;
  feedback: string | null;
}

const activeTab = ref("roll-call");
const classes = ref<ClassItem[]>([]);
const selectedClass = ref<number | null>(null);
const rollCallDate = ref("");
const rollCallPeriod = ref(1);

const students = ref<StudentItem[]>([]);
const leaves = ref<LeaveRecord[]>([]);
const classLogs = ref<any[]>([]);

const loading = ref(false);
const rollCallLoading = ref(false);

const showApproveDialog = ref(false);
const activeLeave = ref<LeaveRecord | null>(null);
const approveForm = ref({
  status: "approved",
  feedback: "",
});
const approveLoading = ref(false);

const PERIODS = [1, 2, 3, 4, 5, 6, 7, 8];

const STATUS_MAP: Record<string, { text: string; type: string }> = {
  present: { text: "出勤", type: "success" },
  tardy: { text: "迟到", type: "warning" },
  absent: { text: "缺勤", type: "danger" },
  leave: { text: "请假", type: "info" },
};

const LEAVE_STATUS_MAP: Record<string, { text: string; type: string }> = {
  pending: { text: "审核中", type: "warning" },
  approved: { text: "已批准", type: "success" },
  rejected: { text: "已拒绝", type: "danger" },
};

async function loadInitialData() {
  loading.value = true;
  try {
    const clsRes: any = await getTeacherClasses();
    classes.value = clsRes.data?.classes || [];
    if (classes.value.length > 0) {
      selectedClass.value = classes.value[0].id;
      loadClassStudents();
    }
    
    // Default today's date
    const d = new Date();
    rollCallDate.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  } catch (error) {
    console.error(error);
    ElMessage.error("获取班级列表失败");
  } finally {
    loading.value = false;
  }
}

async function loadClassStudents() {
  if (!selectedClass.value) return;
  // We can fetch students in the class
  loading.value = true;
  try {
    // We can reuse the class roster from scores or user management helper
    // Or we fetch from the user service by getting the homeroom student list if they are the homeroom teacher
    // Let's fetch from the homeroom students endpoint directly
    const res: any = await httpGetHomeroomStudents();
    if (res.data && res.data.students) {
      students.value = res.data.students.map((s: any) => ({
        id: s.id,
        name: s.name,
        username: s.username,
        status: "present",
        reason: "",
      }));
    }
  } catch (error) {
    console.error(error);
    // fallback or error
  } finally {
    loading.value = false;
  }
}

// Wrapper for direct import from users api to bypass typescript issues
import { getHomeroomStudentsApi } from "../../api/users";
async function httpGetHomeroomStudents() {
  return getHomeroomStudentsApi();
}

async function handleRollCallSubmit() {
  if (!selectedClass.value) {
    ElMessage.warning("请选择班级");
    return;
  }
  if (!rollCallDate.value) {
    ElMessage.warning("请选择点名日期");
    return;
  }

  rollCallLoading.value = true;
  try {
    await takeRollCall({
      class_id: selectedClass.value,
      date: rollCallDate.value,
      period: rollCallPeriod.value,
      records: students.value.map((s) => ({
        student_id: s.id,
        status: s.status,
        reason: s.reason || undefined,
      })),
    });
    ElMessage.success("点名提交成功！");
    loadLogs();
  } catch (error) {
    console.error(error);
    ElMessage.error("提交点名失败");
  } finally {
    rollCallLoading.value = false;
  }
}

async function loadLeaves() {
  loading.value = true;
  try {
    const res: any = await getTeacherLeaves();
    leaves.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取请假列表失败");
  } finally {
    loading.value = false;
  }
}

async function loadLogs() {
  loading.value = true;
  try {
    const res: any = await getTeacherClassLogs();
    classLogs.value = res.data || [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

function handleTabClick() {
  if (activeTab.value === "roll-call") {
    loadClassStudents();
  } else if (activeTab.value === "leaves") {
    loadLeaves();
  } else if (activeTab.value === "logs") {
    loadLogs();
  }
}

function openApprove(lv: LeaveRecord) {
  activeLeave.value = lv;
  approveForm.value = {
    status: "approved",
    feedback: "",
  };
  showApproveDialog.value = true;
}

async function handleApproveSubmit() {
  if (!activeLeave.value) return;
  approveLoading.value = true;
  try {
    await approveLeaveRequest(activeLeave.value.id, {
      status: approveForm.value.status,
      feedback: approveForm.value.feedback,
    });
    ElMessage.success("请假处理成功");
    showApproveDialog.value = false;
    loadLeaves();
  } catch (error) {
    console.error(error);
    ElMessage.error("处理请假单失败");
  } finally {
    approveLoading.value = false;
  }
}

onMounted(() => {
  loadInitialData();
});
</script>

<template>
  <div class="attendance-manage-page" v-loading="loading">
    <div class="custom-tab-menu">
      <el-radio-group v-model="activeTab" @change="handleTabClick" style="margin-bottom: 20px">
        <el-radio-button value="roll-call">课堂点名</el-radio-button>
        <el-radio-button value="leaves">请假审批</el-radio-button>
        <el-radio-button value="logs">考勤日志</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 课堂点名 Tab -->
    <div v-if="activeTab === 'roll-call'" class="roll-call-panel">
      <div class="filter-bar">
        <div class="filter-item">
          <span class="lbl">考勤日期:</span>
          <el-date-picker v-model="rollCallDate" type="date" value-format="YYYY-MM-DD" placeholder="点名日期" style="width: 160px" />
        </div>
        <div class="filter-item">
          <span class="lbl">课节节次:</span>
          <el-select v-model="rollCallPeriod" placeholder="选择节次" style="width: 120px">
            <el-option v-for="p in PERIODS" :key="p" :label="`第 ${p} 节`" :value="p" />
          </el-select>
        </div>
      </div>

      <div class="roster-table-wrapper" v-if="students.length > 0">
        <el-table :data="students" style="width: 100%" class="custom-table">
          <el-table-column prop="username" label="学号" width="120" />
          <el-table-column prop="name" label="姓名" width="120">
            <template #default="{ row }">
              <strong>{{ row.name }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="出勤状态" min-width="260">
            <template #default="{ row }">
              <el-radio-group v-model="row.status" size="small">
                <el-radio-button value="present">出勤</el-radio-button>
                <el-radio-button value="tardy">迟到</el-radio-button>
                <el-radio-button value="absent">缺勤</el-radio-button>
                <el-radio-button value="leave">请假</el-radio-button>
              </el-radio-group>
            </template>
          </el-table-column>
          <el-table-column label="备注说明" min-width="180">
            <template #default="{ row }">
              <el-input v-model="row.reason" placeholder="选填，如迟到原因或备注" size="small" />
            </template>
          </el-table-column>
        </el-table>

        <div class="submit-action-row">
          <el-button type="primary" :icon="Checked" :loading="rollCallLoading" @click="handleRollCallSubmit">
            保存并提交今日考勤
          </el-button>
        </div>
      </div>
      <el-empty description="未找到本班学生信息，请确认您是否是班主任" v-else />
    </div>

    <!-- 请假审批 Tab -->
    <div v-else-if="activeTab === 'leaves'" class="leaves-panel">
      <el-empty description="暂无待审批的请假单" v-if="leaves.length === 0" />
      <el-table :data="leaves" style="width: 100%" class="custom-table" v-else>
        <el-table-column prop="student_name" label="学生姓名" width="110">
          <template #default="{ row }">
            <strong>{{ row.student_name }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="请假起止时间" width="220">
          <template #default="{ row }">
            {{ row.start_date }} 至 {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="请假原因" min-width="180" show-overflow-tooltip />
        <el-table-column label="审批状态" width="100">
          <template #default="{ row }">
            <el-tag :type="LEAVE_STATUS_MAP[row.status]?.type || 'info'" size="small">
              {{ LEAVE_STATUS_MAP[row.status]?.text || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              plain
              @click="openApprove(row)"
            >
              去审批
            </el-button>
            <span class="text-muted" v-else>已完成</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 考勤日志 Tab -->
    <div v-else-if="activeTab === 'logs'" class="logs-panel">
      <el-empty description="暂无考勤历史记录" v-if="classLogs.length === 0" />
      <el-table :data="classLogs" style="width: 100%" class="custom-table" v-else>
        <el-table-column prop="date" label="考勤日期" width="120" />
        <el-table-column prop="period" label="节次" width="80">
          <template #default="{ row }">
            第 {{ row.period }} 节
          </template>
        </el-table-column>
        <el-table-column prop="student_name" label="姓名" width="110" />
        <el-table-column label="出勤状态" width="100">
          <template #default="{ row }">
            <el-tag :type="STATUS_MAP[row.status]?.type || 'info'" size="small">
              {{ STATUS_MAP[row.status]?.text || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="备注/说明" min-width="160" show-overflow-tooltip />
      </el-table>
    </div>

    <!-- 请假审批 Dialog -->
    <el-dialog
      v-model="showApproveDialog"
      title="请假申请审批"
      width="480px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <div v-if="activeLeave" class="approve-details">
        <p><strong>学生：</strong>{{ activeLeave.student_name }}</p>
        <p><strong>起止时间：</strong>{{ activeLeave.start_date }} 至 {{ activeLeave.end_date }}</p>
        <p><strong>请假原因：</strong>{{ activeLeave.reason }}</p>

        <el-form :model="approveForm" label-position="top" style="margin-top: 16px">
          <el-form-item label="审批意见" required>
            <el-radio-group v-model="approveForm.status">
              <el-radio-button value="approved">同意</el-radio-button>
              <el-radio-button value="rejected">拒绝</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="反馈评语">
            <el-input
              v-model="approveForm.feedback"
              type="textarea"
              :rows="3"
              placeholder="请输入反馈评语或意见说明（选填）"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showApproveDialog = false">取消</el-button>
          <el-button type="primary" :loading="approveLoading" @click="handleApproveSubmit">确认提交</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.attendance-manage-page {
  width: 100%;
}
.filter-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  background: var(--color-bg-content);
  padding: 14px 20px;
  border-radius: 8px;
  border: 1px solid var(--color-border-light);
}
.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-item .lbl {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.roster-table-wrapper {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.submit-action-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.text-muted {
  font-size: 12px;
  color: var(--color-text-light);
}

/* Dialog info styling */
.approve-details p {
  font-size: 13px;
  color: var(--color-text);
  line-height: 1.6;
  margin: 6px 0;
}
.approve-details strong {
  color: var(--color-text-secondary);
}

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
