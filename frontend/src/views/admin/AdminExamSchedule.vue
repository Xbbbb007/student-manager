<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getTeacherClasses } from "../../api/scores";
import {
  getAdminExamSchedules,
  batchCreateExamSchedules,
  detectExamConflicts,
  deleteExamSchedule,
} from "../../api/exam_schedule";
import { Plus, Warning, Refresh, Delete } from "@element-plus/icons-vue";

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
  status: string;
  average_score: number | null;
}

interface ClassOption {
  id: number;
  name: string;
}

interface ConflictExam {
  id: number;
  name: string;
  subject: string;
  subject_name: string;
  start_time: string;
  end_time: string;
  location: string;
}

interface ConflictItem {
  date: string;
  class_id: number;
  class_name: string;
  exams: ConflictExam[];
}

const schedules = ref<ExamScheduleItem[]>([]);
const classes = ref<ClassOption[]>([]);
const conflicts = ref<ConflictItem[]>([]);
const loading = ref(false);
const showBatchDialog = ref(false);
const batchLoading = ref(false);
const conflictLoading = ref(false);

const filterClassId = ref<number | null>(null);
const filterSubject = ref<string>("");

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const form = ref({
  name: "",
  class_ids: [] as number[],
  subject: "chinese",
  exam_date: "",
  start_time: "",
  end_time: "",
  location: "在线测试",
});

const filteredSchedules = computed(() => {
  return schedules.value.filter((s) => {
    const matchClass = !filterClassId.value || s.class_id === filterClassId.value;
    const matchSubj = !filterSubject.value || s.subject === filterSubject.value;
    return matchClass && matchSubj;
  });
});

async function loadData() {
  loading.value = true;
  try {
    const [schedRes, clsRes]: any = await Promise.all([
      getAdminExamSchedules(),
      getTeacherClasses(),
    ]);
    schedules.value = schedRes.data || [];
    classes.value = clsRes.data?.classes || [];
    runConflictCheck();
  } catch (error) {
    console.error(error);
    ElMessage.error("获取测试日程概况失败");
  } finally {
    loading.value = false;
  }
}

async function runConflictCheck() {
  conflictLoading.value = true;
  try {
    const res: any = await detectExamConflicts();
    conflicts.value = res.data || [];
  } catch (error) {
    console.error(error);
  } finally {
    conflictLoading.value = false;
  }
}

async function handleBatchCreate() {
  if (!form.value.name.trim()) return ElMessage.warning("请填写测试名称");
  if (!form.value.class_ids || form.value.class_ids.length === 0) return ElMessage.warning("请选择至少一个班级");
  if (!form.value.exam_date) return ElMessage.warning("请选择日期");
  if (!form.value.start_time || !form.value.end_time) return ElMessage.warning("请选择测试具体起止时间");
  if (!form.value.location.trim()) return ElMessage.warning("请填写测试地点");

  batchLoading.value = true;
  try {
    const dateObj = new Date(form.value.exam_date);
    const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, "0")}-${String(dateObj.getDate()).padStart(2, "0")}`;

    await batchCreateExamSchedules({
      class_ids: form.value.class_ids,
      name: form.value.name,
      subject: form.value.subject,
      exam_date: dateStr,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      location: form.value.location,
    });

    ElMessage.success("批量发布测试成功！");
    showBatchDialog.value = false;
    form.value = {
      name: "",
      class_ids: [],
      subject: "chinese",
      exam_date: "",
      start_time: "",
      end_time: "",
      location: "在线测试",
    };
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("批量发布小测失败");
  } finally {
    batchLoading.value = false;
  }
}

async function handleDelete(item: ExamScheduleItem) {
  try {
    await ElMessageBox.confirm(`确定要删除 ${item.class_name} 的 ${item.name} 测试吗？`, "提示", {
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
  <div class="admin-exam-schedule" v-loading="loading">
    
    <!-- 顶栏冲突预警卡片 -->
    <div class="conflict-alert-banner" v-if="conflicts.length > 0">
      <div class="banner-header">
        <span class="warning-title">
          <el-icon><Warning /></el-icon>
          日程冲突警报（同一天安排了多场测试，发现 {{ conflicts.length }} 处！）
        </span>
        <el-button size="small" :icon="Refresh" @click="runConflictCheck" :loading="conflictLoading">重新检测</el-button>
      </div>
      <div class="conflict-list">
        <div 
          v-for="(cf, idx) in conflicts" 
          :key="idx" 
          class="conflict-item-card"
        >
          <div class="cf-meta">
            <strong>{{ cf.class_name }}</strong> 在 <strong>{{ cf.date }}</strong> 安排了多场测试：
          </div>
          <div class="cf-exams">
            <span 
              v-for="ex in cf.exams" 
              :key="ex.id" 
              class="cf-badge"
            >
              {{ ex.subject_name }} ({{ ex.start_time }}-{{ ex.end_time }}) @ {{ ex.location }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能按钮与筛选栏 -->
    <div class="actions-filter-bar">
      <div class="filter-left">
        <el-form :inline="true" size="default">
          <el-form-item label="班级">
            <el-select v-model="filterClassId" placeholder="全部班级" clearable style="width: 150px">
              <el-option 
                v-for="c in classes" 
                :key="c.id" 
                :label="c.name" 
                :value="c.id" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="学科">
            <el-select v-model="filterSubject" placeholder="全部学科" clearable style="width: 130px">
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
      <el-button type="primary" :icon="Plus" @click="showBatchDialog = true">批量测试发布</el-button>
    </div>

    <!-- 测试日程数据表格 -->
    <div class="table-card">
      <el-table :data="filteredSchedules" style="width: 100%" class="custom-table">
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
        <el-table-column label="具体时间" width="140">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="测试形式" width="140" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', row.status]">
              {{ row.status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="测试均分" width="100">
          <template #default="{ row }">
            <strong class="grade-text" v-if="row.status === '已结束'">{{ row.average_score !== null ? `${row.average_score}分` : '-' }}</strong>
            <span class="text-muted" v-else>未结束</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 批量发布 Dialog -->
    <el-dialog
      v-model="showBatchDialog"
      title="批量测试发布"
      width="540px"
      destroy-on-close
      append-to-body
      class="custom-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="测试名称" required>
          <el-input v-model="form.name" placeholder="如：第三单元课堂阶段摸底小测" />
        </el-form-item>
        <el-form-item label="选择班级（可多选）" required>
          <el-select 
            v-model="form.class_ids" 
            placeholder="请勾选本次测试涵盖的班级" 
            multiple 
            collapse-tags 
            collapse-tags-tooltip 
            style="width: 100%"
          >
            <el-option 
              v-for="c in classes" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" required>
          <el-select v-model="form.subject" placeholder="选择科目" style="width: 100%">
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
        <el-form-item label="测试形式" required>
          <el-input v-model="form.location" placeholder="如：在线测试" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchDialog = false">取消</el-button>
          <el-button type="primary" :loading="batchLoading" @click="handleBatchCreate">确定发布</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-exam-schedule {
  width: 100%;
}

/* 冲突预警大横幅 */
.conflict-alert-banner {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
}
.banner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.warning-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-danger);
}
.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.conflict-item-card {
  font-size: 13px;
  color: var(--color-text);
  background: #ffffff;
  border-left: 4px solid var(--color-danger);
  padding: 8px 12px;
  border-radius: 4px;
}
.cf-meta {
  margin-bottom: 6px;
}
.cf-exams {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.cf-badge {
  font-size: 11px;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.08);
  color: var(--color-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
}

/* 筛选与按钮 */
.actions-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  padding: 14px 18px 0;
  margin-bottom: 20px;
}
.filter-left :deep(.el-form-item) {
  margin-bottom: 14px;
}

/* 表格 */
.table-card {
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

.grade-text {
  color: var(--color-success);
  font-weight: 700;
}
.text-muted {
  color: var(--color-text-light);
  font-size: 12px;
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
</style>
