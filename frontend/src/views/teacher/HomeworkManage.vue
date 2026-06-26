<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useUserStore } from "../../stores/user";
import { getTeacherClasses } from "../../api/scores";
import {
  createHomework,
  getTeacherHomeworks,
  getHomeworkSubmissions,
  gradeSubmission,
} from "../../api/homework";
import { Plus, EditPen } from "@element-plus/icons-vue";

const userStore = useUserStore();
const userInfo = userStore.userInfo;

interface HomeworkListItem {
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
  total_students: number;
  submitted_count: number;
  graded_count: number;
}

interface SubmissionItem {
  student_id: number;
  student_name: string;
  student_username: string;
  submission_id: number | null;
  content: string | null;
  submitted_at: string | null;
  grade: number | null;
  feedback: string | null;
  status: "unsubmitted" | "submitted" | "graded";
}

interface TeacherClass {
  id: number;
  name: string;
  student_count: number;
}

const homeworks = ref<HomeworkListItem[]>([]);
const classes = ref<TeacherClass[]>([]);
const loading = ref(false);

// Assign Homework Dialog state
const showCreateDialog = ref(false);
const createLoading = ref(false);
const newHw = ref({
  title: "",
  description: "",
  class_ids: [] as number[],
  subject: userInfo?.subject || "chinese",
  due_date: "",
});

// Grading Dialog/Drawer state
const showGradeDialog = ref(false);
const activeHw = ref<HomeworkListItem | null>(null);
const submissions = ref<SubmissionItem[]>([]);
const submissionsLoading = ref(false);

// Individual grading modal
const showSingleGradeModal = ref(false);
const activeSub = ref<SubmissionItem | null>(null);
const gradeVal = ref<number | null>(null);
const feedbackVal = ref("");
const gradeLoading = ref(false);

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

async function loadInitialData() {
  loading.value = true;
  try {
    const [hwRes, clsRes]: any = await Promise.all([
      getTeacherHomeworks(),
      getTeacherClasses(),
    ]);
    homeworks.value = hwRes.data || [];
    classes.value = clsRes.data?.classes || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取数据失败");
  } finally {
    loading.value = false;
  }
}

async function handleAssignHomework() {
  if (!newHw.value.title.trim()) {
    ElMessage.warning("请填写作业标题");
    return;
  }
  if (!newHw.value.class_ids || newHw.value.class_ids.length === 0) {
    ElMessage.warning("请选择班级");
    return;
  }
  if (!newHw.value.due_date) {
    ElMessage.warning("请选择截止日期");
    return;
  }

  createLoading.value = true;
  try {
    const promises = newHw.value.class_ids.map((cid) => {
      return createHomework({
        title: newHw.value.title,
        description: newHw.value.description,
        subject: newHw.value.subject,
        class_id: cid,
        due_date: new Date(newHw.value.due_date).toISOString(),
      });
    });
    await Promise.all(promises);
    ElMessage.success("作业布置成功！");
    showCreateDialog.value = false;
    // reset form
    newHw.value = {
      title: "",
      description: "",
      class_ids: [],
      subject: userInfo?.subject || "chinese",
      due_date: "",
    };
    loadInitialData();
  } catch (error) {
    console.error(error);
    ElMessage.error("布置作业失败");
  } finally {
    createLoading.value = false;
  }
}

async function openSubmissions(hw: HomeworkListItem) {
  activeHw.value = hw;
  showGradeDialog.value = true;
  submissionsLoading.value = true;
  try {
    const res: any = await getHomeworkSubmissions(hw.id);
    submissions.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取提交记录失败");
  } finally {
    submissionsLoading.value = false;
  }
}

function openSingleGrade(sub: SubmissionItem) {
  activeSub.value = sub;
  gradeVal.value = sub.grade;
  feedbackVal.value = sub.feedback || "";
  showSingleGradeModal.value = true;
}

async function handleSaveGrade() {
  if (!activeSub.value || !activeSub.value.submission_id) return;
  if (gradeVal.value === null || gradeVal.value < 0 || gradeVal.value > 100) {
    ElMessage.warning("请输入有效的得分(0-100)");
    return;
  }

  gradeLoading.value = true;
  try {
    await gradeSubmission(activeSub.value.submission_id, gradeVal.value, feedbackVal.value);
    ElMessage.success("批改保存成功");
    showSingleGradeModal.value = false;
    // Refresh submissions list and main homeworks list
    if (activeHw.value) {
      openSubmissions(activeHw.value);
    }
    loadInitialData();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存批改失败");
  } finally {
    gradeLoading.value = false;
  }
}

function formatTime(timeStr: string) {
  if (!timeStr) return "-";
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

onMounted(() => {
  loadInitialData();
});
</script>

<template>
  <div class="teacher-homework" v-loading="loading">
    <div class="header-action">
      <h2>作业管理</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">布置作业</el-button>
    </div>

    <!-- 作业列表表格 -->
    <div class="table-container">
      <el-table :data="homeworks" style="width: 100%" class="custom-table">
        <el-table-column prop="title" label="作业标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="class_name" label="班级" width="130" />
        <el-table-column prop="subject" label="科目" width="100">
          <template #default="{ row }">
            {{ SUBJECTS[row.subject] || row.subject }}
          </template>
        </el-table-column>
        <el-table-column label="提交进度" width="160">
          <template #default="{ row }">
            <div class="progress-info">
              <span>{{ row.submitted_count }} / {{ row.total_students }}</span>
              <el-progress 
                :percentage="row.total_students ? Math.round((row.submitted_count / row.total_students) * 100) : 0" 
                :show-text="false"
                status="success"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="已批改数" width="110">
          <template #default="{ row }">
            <span class="graded-cnt">{{ row.graded_count }} / {{ row.submitted_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="截止时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openSubmissions(row)">批改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 布置作业 Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建作业"
      width="540px"
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="newHw" label-position="top">
        <el-form-item label="作业标题" required>
          <el-input v-model="newHw.title" placeholder="如：第三单元乘法口诀课后巩固" />
        </el-form-item>
        <el-form-item label="选择班级" required>
          <el-select v-model="newHw.class_ids" placeholder="请选择分配班级（可多选）" multiple collapse-tags collapse-tags-tooltip style="width: 100%">
            <el-option 
              v-for="c in classes" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" required>
          <el-select v-model="newHw.subject" placeholder="请选择科目" :disabled="!userInfo?.role.includes('admin')">
            <el-option 
              v-for="(val, key) in SUBJECTS" 
              :key="key" 
              :label="val" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" required>
          <el-date-picker
            v-model="newHw.due_date"
            type="datetime"
            placeholder="选择截止日期和时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="作业内容要求">
          <el-input 
            v-model="newHw.description" 
            type="textarea" 
            :rows="5" 
            placeholder="请输入作业具体要求或题目描述..." 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="createLoading" @click="handleAssignHomework">确认发布</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批改作业详情 Drawer/Dialog -->
    <el-dialog
      v-model="showGradeDialog"
      :title="activeHw ? `作业批改 - ${activeHw.title}` : '作业批改'"
      width="90%"
      style="max-width: 960px;"
      destroy-on-close
      class="custom-dialog"
    >
      <div v-loading="submissionsLoading" class="submissions-container">
        <el-table :data="submissions" style="width: 100%" class="custom-table inner-table">
          <el-table-column prop="student_username" label="学号" width="120" />
          <el-table-column prop="student_name" label="姓名" width="110" />
          <el-table-column label="提交状态" width="110">
            <template #default="{ row }">
              <span :class="['status-tag', row.status]">
                {{ row.status === 'unsubmitted' ? '未提交' : (row.status === 'submitted' ? '待批改' : '已批改') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="160">
            <template #default="{ row }">
              {{ row.submitted_at ? formatTime(row.submitted_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="grade" label="得分" width="90">
            <template #default="{ row }">
              <span class="score-val" v-if="row.status === 'graded'">{{ row.grade }}</span>
              <span class="score-placeholder" v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="feedback" label="批语" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="row.status !== 'unsubmitted'" 
                type="primary" 
                link
                :icon="EditPen"
                @click="openSingleGrade(row)"
              >
                {{ row.status === 'graded' ? '重新批改' : '去批改' }}
              </el-button>
              <span v-else class="text-muted">无提交</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 单个作业批改弹出框 -->
    <el-dialog
      v-model="showSingleGradeModal"
      title="作业详情与批改"
      width="600px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <div v-if="activeSub" class="single-grade-box">
        <div class="stu-info">
          <span>学生：<strong>{{ activeSub.student_name }}</strong> ({{ activeSub.student_username }})</span>
        </div>
        <div class="content-box">
          <div class="lbl">提交内容：</div>
          <div class="txt">{{ activeSub.content }}</div>
        </div>

        <el-form label-position="top" class="grade-form">
          <el-form-item label="打分 (0 - 100)" required>
            <el-input-number 
              v-model="gradeVal" 
              :min="0" 
              :max="100" 
              :precision="1"
              style="width: 160px"
            />
          </el-form-item>
          <el-form-item label="批改评语">
            <el-input 
              v-model="feedbackVal" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入鼓励的评语或改进建议..." 
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showSingleGradeModal = false">取消</el-button>
          <el-button type="primary" :loading="gradeLoading" @click="handleSaveGrade">保存批改</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.teacher-homework {
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

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.progress-info span {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.graded-cnt {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
}

/* Status tags for submissions list */
.status-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 12px;
}
.status-tag.unsubmitted {
  background: rgba(107, 114, 128, 0.1);
  color: var(--color-info);
}
.status-tag.submitted {
  background: rgba(232, 168, 56, 0.1);
  color: var(--color-warning);
}
.status-tag.graded {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.score-val {
  font-weight: 700;
  color: var(--color-success);
}
.score-placeholder {
  color: var(--color-text-light);
}

.text-muted {
  font-size: 12px;
  color: var(--color-text-light);
}

/* Dialog Forms Styling */
.custom-dialog :deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Single grade box styling */
.single-grade-box {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.stu-info {
  font-size: 14px;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 8px;
}
.content-box {
  background: rgba(8, 31, 92, 0.02);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  padding: 12px 16px;
}
.content-box .lbl {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
  font-weight: 700;
}
.content-box .txt {
  font-size: 14px;
  color: var(--color-text);
  line-height: 1.6;
  white-space: pre-wrap;
}
.grade-form {
  margin-top: 10px;
}
</style>
