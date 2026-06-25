<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "../../stores/user";
import { getTeacherClasses } from "../../api/scores";
import {
  getTeacherExamSchedules,
  createExamSchedule,
  updateExamSchedule,
  deleteExamSchedule,
  autoGradeTest,
  getHomeworkSubmissions, // wait, we have a custom test submissions list endpoint!
} from "../../api/exam_schedule";
import http from "../../api/http"; // let's call the test submissions directly or via helper
import { Plus, EditPen, Delete, Checked, User, Trophy } from "@element-plus/icons-vue";

const userStore = useUserStore();
const userInfo = userStore.userInfo;

interface ExamScheduleListItem {
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
  average_score: number | null;
  submitted_count: number;
  total_students: number;
}

interface TestSubmissionItem {
  student_id: number;
  student_name: string;
  student_username: string;
  score: number | null;
  answers: string | null;
  status: string;
}

interface TeacherClass {
  id: number;
  name: string;
}

const schedules = ref<ExamScheduleListItem[]>([]);
const classes = ref<TeacherClass[]>([]);
const loading = ref(false);

const showFormDialog = ref(false);
const submitLoading = ref(false);
const isEdit = ref(false);
const editId = ref<number | null>(null);

const form = ref({
  name: "",
  class_id: null as number | null,
  subject: userInfo?.subject || "chinese",
  exam_date: "",
  start_time: "",
  end_time: "",
  location: "在线测试",
  status: "未开始",
});

// Test results dialog state
const showResultsDialog = ref(false);
const activeTest = ref<ExamScheduleListItem | null>(null);
const testSubmissions = ref<TestSubmissionItem[]>([]);
const resultsLoading = ref(false);

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const STATUS_OPTIONS = ["未开始", "进行中", "已结束"];

async function loadData() {
  loading.value = true;
  try {
    const [schedRes, clsRes]: any = await Promise.all([
      getTeacherExamSchedules(),
      getTeacherClasses(),
    ]);
    schedules.value = schedRes.data || [];
    classes.value = clsRes.data?.classes || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取测试数据失败");
  } finally {
    loading.value = false;
  }
}

function openAddDialog() {
  isEdit.value = false;
  editId.value = null;
  form.value = {
    name: "",
    class_id: null,
    subject: userInfo?.subject || "chinese",
    exam_date: "",
    start_time: "",
    end_time: "",
    location: "在线测试",
    status: "未开始",
  };
  showFormDialog.value = true;
}

function openEditDialog(item: ExamScheduleListItem) {
  isEdit.value = true;
  editId.value = item.id;
  form.value = {
    name: item.name,
    class_id: item.class_id,
    subject: item.subject,
    exam_date: item.exam_date,
    start_time: item.start_time,
    end_time: item.end_time,
    location: item.location,
    status: item.status,
  };
  showFormDialog.value = true;
}

async function handleSaveSchedule() {
  if (!form.value.name.trim()) return ElMessage.warning("请填写测试名称");
  if (!form.value.class_id) return ElMessage.warning("请选择班级");
  if (!form.value.exam_date) return ElMessage.warning("请选择日期");
  if (!form.value.start_time || !form.value.end_time) return ElMessage.warning("请填写起止时间");

  submitLoading.value = true;
  try {
    const dateObj = new Date(form.value.exam_date);
    const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, "0")}-${String(dateObj.getDate()).padStart(2, "0")}`;

    const payload = {
      ...form.value,
      exam_date: dateStr,
    };

    if (isEdit.value && editId.value !== null) {
      await updateExamSchedule(editId.value, payload);
      ElMessage.success("测试日程更新成功");
    } else {
      await createExamSchedule(payload);
      ElMessage.success("测试日程发布成功");
    }
    showFormDialog.value = false;
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存失败");
  } finally {
    submitLoading.value = false;
  }
}

async function handleAutoGrade(item: ExamScheduleListItem) {
  try {
    await ElMessageBox.confirm(`确定要为 ${item.class_name} 班的所有学生自动评分吗？（该操作将模拟学生答案和测试得分，直接结束本场测试，仅供演示）`, "提示", {
      confirmButtonText: "确定一键打分",
      cancelButtonText: "取消",
      type: "success",
    });

    loading.value = true;
    await autoGradeTest(item.id);
    ElMessage.success("已成功一键自动打分！");
    loadData();
  } catch (error) {
    if (error !== "cancel") {
      console.error(error);
      ElMessage.error("自动打分失败");
    }
    loading.value = false;
  }
}

async function openResults(item: ExamScheduleListItem) {
  activeTest.value = item;
  showResultsDialog.value = true;
  resultsLoading.value = true;
  try {
    const res: any = await http.get(`/exams-schedule/${item.id}/submissions`);
    testSubmissions.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取测试结果失败");
  } finally {
    resultsLoading.value = false;
  }
}

async function handleDelete(item: ExamScheduleListItem) {
  try {
    await ElMessageBox.confirm(`确定要删除 ${item.class_name} 的 ${item.name} 吗？`, "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    
    await deleteExamSchedule(item.id);
    ElMessage.success("删除成功");
    loadData();
  } catch (error) {
    if (error !== "cancel") {
      console.error(error);
      ElMessage.error("删除失败");
    }
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="exam-schedule-manage" v-loading="loading">
    <div class="header-action">
      <h2>课堂测试管理</h2>
      <el-button type="primary" :icon="Plus" @click="openAddDialog">发布新小测</el-button>
    </div>

    <!-- 测试日程表格 -->
    <div class="table-container">
      <el-table :data="schedules" style="width: 100%" class="custom-table">
        <el-table-column prop="name" label="测试名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="class_name" label="班级" width="130" />
        <el-table-column prop="subject" label="科目" width="100">
          <template #default="{ row }">
            {{ SUBJECTS[row.subject] || row.subject }}
          </template>
        </el-table-column>
        <el-table-column label="测试日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.exam_date) }}
          </template>
        </el-table-column>
        <el-table-column label="测试时间" width="140">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', row.status]">
              {{ row.status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="平均分" width="95">
          <template #default="{ row }">
            <span class="avg-score" v-if="row.status === '已结束'">
              {{ row.average_score !== null ? `${row.average_score}分` : '-' }}
            </span>
            <span class="pending-lbl" v-else>未结束</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status !== '已结束'"
              type="success" 
              size="small" 
              :icon="Checked"
              @click="handleAutoGrade(row)"
            >
              自动打分
            </el-button>
            <el-button 
              v-else
              type="warning" 
              size="small" 
              :icon="Trophy"
              @click="openResults(row)"
            >
              测试成绩
            </el-button>

            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 表单 Dialog -->
    <el-dialog
      v-model="showFormDialog"
      :title="isEdit ? '编辑小测日程' : '发布小测日程'"
      width="500px"
      destroy-on-close
      append-to-body
      class="custom-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="测试名称" required>
          <el-input v-model="form.name" placeholder="如：第三章一元一次方程课堂测试" />
        </el-form-item>
        <el-form-item label="选择班级" required>
          <el-select v-model="form.class_id" placeholder="请选择测试班级" style="width: 100%">
            <el-option 
              v-for="c in classes" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" required>
          <el-select v-model="form.subject" placeholder="请选择科目" style="width: 100%" :disabled="!userInfo?.role.includes('admin')">
            <el-option 
              v-for="(val, key) in SUBJECTS" 
              :key="key" 
              :label="val" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试日期" required>
          <el-date-picker
            v-model="form.exam_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <div class="time-range-row">
          <el-form-item label="开始时间" required style="flex: 1">
            <el-time-select
              v-model="form.start_time"
              start="08:00"
              step="00:10"
              end="18:00"
              placeholder="开始时间"
            />
          </el-form-item>
          <el-form-item label="结束时间" required style="flex: 1">
            <el-time-select
              v-model="form.end_time"
              start="08:30"
              step="00:10"
              end="20:00"
              placeholder="结束时间"
            />
          </el-form-item>
        </div>
        <el-form-item label="测试方式" required>
          <el-input v-model="form.location" placeholder="如：在线测试 / 线上机房" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option 
              v-for="st in STATUS_OPTIONS" 
              :key="st" 
              :label="st" 
              :value="st" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showFormDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSaveSchedule">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 测试结果 Dialog -->
    <el-dialog
      v-model="showResultsDialog"
      :title="activeTest ? `测试成绩报告 - ${activeTest.name}` : '测试成绩报告'"
      width="680px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <div v-loading="resultsLoading" class="results-box">
        <el-table :data="testSubmissions" style="width: 100%" class="custom-table inner-table">
          <el-table-column prop="student_username" label="学号" width="130" />
          <el-table-column prop="student_name" label="学生姓名" width="120" />
          <el-table-column label="测试状态" width="120">
            <template #default="{ row }">
              <span :class="['status-tag', row.status]">
                {{ row.status === 'graded' ? '已评分' : (row.status === 'submitted' ? '待评分' : '缺考') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="得分" width="100">
            <template #default="{ row }">
              <strong class="grade-text" v-if="row.status === 'graded'">{{ row.score }} 分</strong>
              <span class="text-muted" v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="answers" label="作答内容" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="showResultsDialog = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.exam-schedule-manage {
  width: 100%;
}
.header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-action h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}
.table-container {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.status-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 12px;
}
.status-tag.未开始 {
  background: rgba(51, 78, 172, 0.08);
  color: var(--color-primary);
}
.status-tag.进行中 {
  background: rgba(232, 168, 56, 0.12);
  color: var(--color-warning);
}
.status-tag.已结束 {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
.status-tag.graded {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
.status-tag.submitted {
  background: rgba(232, 168, 56, 0.1);
  color: var(--color-warning);
}
.status-tag.unsubmitted {
  background: rgba(107, 114, 128, 0.1);
  color: var(--color-text-light);
}

.avg-score {
  font-weight: 700;
  color: var(--color-success);
}
.grade-text {
  color: var(--color-success);
  font-weight: 700;
}
.pending-lbl {
  font-size: 12px;
  color: var(--color-text-light);
}

.time-range-row {
  display: flex;
  gap: 16px;
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
.text-muted {
  color: var(--color-text-light);
}
</style>
