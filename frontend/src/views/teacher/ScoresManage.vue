<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "../../stores/user";
import {
  getExams,
  getClassScores,
  batchSaveScores,
  createExam,
  getTeacherClasses,
  getTeacherExams,
  getTeacherDashboard,
} from "../../api/scores";
import { ElMessage } from "element-plus";

const userStore = useUserStore();
const userInfo = userStore.userInfo;

// ─── 权限 ────────────────────────────────────
const teacherSubject = ref<string | null>(null);
const isAdmin = ref(false);

// ─── 类型 ────────────────────────────────────
interface TeacherClass {
  id: number;
  name: string;
  section: string;
  grade: string;
  student_count: number;
  homeroom_teacher_id?: number | null;
}
interface ExamGroup {
  name: string;
  exam_date: string | null;
  exam_class_ids: Array<{ exam_id: number; class_id: number }>;
}
interface StudentScore {
  student_id: number;
  student_name: string;
  username: string;
  score: number | null;
  class_rank: number | null;
  school_rank: number | null;
}

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};
const SUBJECT_KEYS = Object.keys(SUBJECTS);

// ─── 状态 ────────────────────────────────────
const teacherClasses = ref<TeacherClass[]>([]);
const examGroups = ref<ExamGroup[]>([]);
const dashboard = ref<any>(null);
const students = ref<StudentScore[]>([]);
const editingScores = ref<Record<number, number>>({});

const selectedClassId = ref<number | "overall">("overall");
const selectedExamName = ref<string>("");
const selectedSubject = ref<string>("");

const loading = ref(false);
const saving = ref(false);
const showNewExamDialog = ref(false);
const newExamName = ref("");
const newExamDate = ref("");

// ─── 计算属性 ────────────────────────────────
const isOverall = computed(() => selectedClassId.value === "overall");

const currentClassIds = computed<number[]>(() => {
  if (isOverall.value) return teacherClasses.value.map((c) => c.id);
  return [selectedClassId.value as number];
});

const currentClass = computed(() =>
  teacherClasses.value.find((c) => c.id === selectedClassId.value)
);

// 当前选中考试在所选班级中的 exam_ids
const currentExamIds = computed<string>(() => {
  const group = examGroups.value.find(
    (g) => g.name === selectedExamName.value
  );
  if (!group) return "";
  if (isOverall.value) {
    return group.exam_class_ids.map((e) => e.exam_id).join(",");
  }
  const cid = selectedClassId.value as number;
  const match = group.exam_class_ids.find((e) => e.class_id === cid);
  return match ? String(match.exam_id) : "";
});

// 用于新建考试的 class_id（单班视图直接用，总体视图用第一个班）
const newExamClassId = computed(() => {
  if (!isOverall.value) return selectedClassId.value as number;
  return teacherClasses.value[0]?.id ?? null;
});

const filteredSubjects = computed(() => {
  if (isAdmin.value) return SUBJECT_KEYS;
  
  if (selectedClassId.value !== "overall") {
    const cls = teacherClasses.value.find((c) => c.id === selectedClassId.value);
    if (cls && cls.homeroom_teacher_id === userInfo?.id) {
      return SUBJECT_KEYS;
    }
  }

  if (teacherSubject.value && SUBJECT_KEYS.includes(teacherSubject.value)) {
    return [teacherSubject.value];
  }
  return SUBJECT_KEYS;
});

const hasUnsavedChanges = computed(
  () => Object.keys(editingScores.value).length > 0
);

// ─── 数据加载 ────────────────────────────────
async function loadTeacherClasses() {
  try {
    const res: any = await getTeacherClasses();
    teacherClasses.value = res.data?.classes || [];
  } catch (e) {
    console.error("加载班级失败", e);
  }
}

async function loadExamGroups() {
  if (currentClassIds.value.length === 0) {
    examGroups.value = [];
    return;
  }
  try {
    const res: any = await getTeacherExams(
      currentClassIds.value.join(",")
    );
    examGroups.value = res.data || [];
    // 自动选中最新一次考试（列表末尾）
    if (examGroups.value.length > 0) {
      selectedExamName.value = examGroups.value[examGroups.value.length - 1].name;
    }
  } catch {
    examGroups.value = [];
  }
}

async function loadDashboard() {
  if (!currentExamIds.value || !selectedSubject.value) {
    dashboard.value = null;
    return;
  }
  loading.value = true;
  try {
    const res: any = await getTeacherDashboard(
      currentExamIds.value,
      selectedSubject.value
    );
    dashboard.value = res.data || null;

    // 单班视图额外加载成绩编辑表
    if (!isOverall.value && dashboard.value?.summary) {
      await loadClassScores();
    } else {
      students.value = [];
      editingScores.value = {};
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "加载仪表盘失败");
    dashboard.value = null;
  } finally {
    loading.value = false;
  }
}

async function loadClassScores() {
  const examId = parseInt(currentExamIds.value);
  if (!examId || !selectedSubject.value) {
    students.value = [];
    return;
  }
  try {
    const res: any = await getClassScores(examId, selectedSubject.value);
    students.value = res.data?.students || [];
    editingScores.value = {};
  } catch {
    students.value = [];
  }
}

// ─── 事件处理 ────────────────────────────────
function handleClassChange() {
  dashboard.value = null;
  students.value = [];
  editingScores.value = {};
  
  if (!filteredSubjects.value.includes(selectedSubject.value)) {
    if (filteredSubjects.value.length > 0) {
      selectedSubject.value = filteredSubjects.value[0];
    } else {
      selectedSubject.value = "";
    }
  }

  if (currentExamIds.value && selectedSubject.value) {
    loadDashboard();
  }
}

function handleExamChange() {
  dashboard.value = null;
  students.value = [];
  editingScores.value = {};
  if (selectedExamName.value && selectedSubject.value) {
    loadDashboard();
  }
}

function handleSubjectChange() {
  if (currentExamIds.value) {
    loadDashboard();
  }
}

// ─── 成绩编辑 ────────────────────────────────
async function saveScores() {
  const ids = Object.keys(editingScores.value);
  if (ids.length === 0) {
    ElMessage.info("没有需要保存的修改");
    return;
  }
  saving.value = true;
  try {
    const examId = parseInt(currentExamIds.value);
    const items = ids.map((sid) => ({
      student_id: parseInt(sid),
      exam_id: examId,
      subject: selectedSubject.value,
      score: editingScores.value[parseInt(sid)],
    }));
    await batchSaveScores(items);
    ElMessage.success(`已保存 ${items.length} 条成绩`);
    editingScores.value = {};
    await loadDashboard();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

async function handleNewExam() {
  if (!newExamName.value) {
    ElMessage.warning("请输入考试名称");
    return;
  }
  if (!newExamClassId.value) {
    ElMessage.warning("请先选择班级");
    return;
  }
  try {
    await createExam({
      name: newExamName.value,
      class_id: newExamClassId.value,
      exam_date: newExamDate.value || undefined,
    });
    ElMessage.success("考试创建成功");
    showNewExamDialog.value = false;
    newExamName.value = "";
    newExamDate.value = "";
    await loadExamGroups();
    if (selectedExamName.value) {
      await loadDashboard();
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建考试失败");
  }
}

// ─── 工具函数 ────────────────────────────────
function getScoreDisplay(studentId: number): number | undefined {
  if (editingScores.value[studentId] !== undefined) {
    return editingScores.value[studentId];
  }
  const s = students.value.find((s) => s.student_id === studentId);
  return s?.score ?? undefined;
}

function rankBadgeClass(rank: number | null): string {
  if (!rank) return "";
  if (rank <= 10) return "rank-top";
  if (rank <= 20) return "rank-mid";
  return "rank-low";
}

function formatChange(val: number | null): string {
  if (val === null || val === undefined) return "—";
  if (val > 0) return `+${val}`;
  return `${val}`;
}

function changeClass(val: number | null): string {
  if (val === null || val === undefined) return "change-flat";
  return val > 0 ? "change-up" : val < 0 ? "change-down" : "change-flat";
}

// ─── 初始化 ──────────────────────────────────
onMounted(async () => {
  isAdmin.value = userInfo?.role === "admin";
  if (!isAdmin.value && userInfo?.subject) {
    teacherSubject.value = userInfo.subject;
  }

  await loadTeacherClasses();
  if (teacherClasses.value.length > 0) {
    await loadExamGroups();
    if (examGroups.value.length > 0 && filteredSubjects.value.length > 0) {
      selectedSubject.value = filteredSubjects.value[0];
      await loadDashboard();
    }
  }
});
</script>

<template>
  <div class="scores-manage" v-loading="loading">
    <!-- ── 筛选栏 ── -->
    <div class="filter-bar">
      <div class="filter-item">
        <label>班级</label>
        <el-select
          v-model="selectedClassId"
          @change="handleClassChange"
          style="width: 200px"
        >
          <el-option label="📊 总体" value="overall" />
          <el-option
            v-for="c in teacherClasses"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </div>
      <div class="filter-item">
        <label>考试</label>
        <el-select
          v-model="selectedExamName"
          @change="handleExamChange"
          placeholder="选择考试"
          style="width: 200px"
        >
          <el-option
            v-for="e in examGroups"
            :key="e.name"
            :label="e.exam_date ? `${e.name}（${e.exam_date}）` : e.name"
            :value="e.name"
          />
        </el-select>
      </div>
      <div class="filter-item">
        <label>科目</label>
        <el-select
          v-model="selectedSubject"
          @change="handleSubjectChange"
          style="width: 140px"
        >
          <el-option
            v-for="k in filteredSubjects"
            :key="k"
            :label="SUBJECTS[k]"
            :value="k"
          />
        </el-select>
      </div>
      <div style="flex: 1"></div>
      <el-button @click="showNewExamDialog = true" size="small">
        + 新建考试
      </el-button>
      <el-button
        v-if="!isOverall && hasUnsavedChanges"
        type="primary"
        :loading="saving"
        @click="saveScores"
        size="small"
      >
        保存 ({{ Object.keys(editingScores).length }})
      </el-button>
    </div>

    <!-- ════════════════════════════════════════ -->
    <!--          总体视图                        -->
    <!-- ════════════════════════════════════════ -->
    <div v-if="isOverall && dashboard?.summary" class="view-content">
      <!-- 概览横幅 -->
      <div class="overall-banner">
        <div>
          <div class="banner-label">当前查看</div>
          <div class="banner-title">
            {{ teacherClasses[0]?.grade || '' }} · 总体概览
          </div>
        </div>
        <div style="margin-left: auto; text-align: right">
          <div class="banner-label">参考总人数</div>
          <div class="banner-title">
            {{ dashboard.summary.total_students }}<span class="banner-unit"> 人</span>
          </div>
        </div>
      </div>

      <!-- 两班对比 -->
      <div v-if="dashboard.comparison?.length" class="compare-row">
        <div v-for="(item, idx) in dashboard.comparison" :key="item.class_id" class="compare-card">
          <div class="compare-card-title">
            <span class="dot" :class="idx === 0 ? 'dot-a' : 'dot-b'"></span>
            {{ item.class_name }}
          </div>
          <div class="compare-grid">
            <div class="compare-stat">
              <span class="label">平均分</span>
              <span class="val">{{ item.avg_score }}</span>
            </div>
            <div class="compare-stat">
              <span class="label">最高分</span>
              <span class="val">{{ item.max_score }}</span>
            </div>
            <div class="compare-stat">
              <span class="label">最低分</span>
              <span class="val">{{ item.min_score }}</span>
            </div>
            <div class="compare-stat">
              <span class="label">及格率</span>
              <span class="val">{{ item.pass_rate }}%</span>
            </div>
            <div class="compare-stat">
              <span class="label">优秀率</span>
              <span class="val">{{ item.excellent_rate }}%</span>
            </div>
            <div class="compare-stat">
              <span class="label">参考人数</span>
              <span class="val">{{ item.total_students }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 合计统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-label">平均分</div>
          <div class="stat-value">{{ dashboard.summary.avg_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最高分</div>
          <div class="stat-value">{{ dashboard.summary.max_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最低分</div>
          <div class="stat-value">{{ dashboard.summary.min_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">及格率</div>
          <div class="stat-value">{{ dashboard.summary.pass_rate }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">优秀率</div>
          <div class="stat-value">{{ dashboard.summary.excellent_rate }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">参考人数</div>
          <div class="stat-value">{{ dashboard.summary.total_students }}<span class="unit">人</span></div>
        </div>
      </div>

      <!-- 前十名 + 波动 -->
      <div class="two-col">
        <div class="section">
          <div class="section-header">
            <div class="section-title"><span class="icon icon-gold">★</span>年级前十名</div>
            <span class="section-sub">按{{ SUBJECTS[selectedSubject] }}成绩排序</span>
          </div>
          <el-table :data="dashboard.top_students" size="small" stripe>
            <el-table-column type="index" label="#" width="44">
              <template #default="{ $index }">
                <span :class="['rank-badge', $index < 3 ? 'rank-top' : $index < 10 ? 'rank-mid' : '']">
                  {{ $index + 1 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="姓名" min-width="80">
              <template #default="{ row }">
                <span class="student-name">{{ row.student_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="学号" width="100">
              <template #default="{ row }">
                <span class="student-id">{{ row.username }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="class_name" label="班级" width="80">
              <template #default="{ row }">
                <span class="class-tag">{{ row.class_name?.replace(/.*(.班)$/, '$1') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="70">
              <template #default="{ row }">
                <span class="score-val">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="变化" width="80">
              <template #default="{ row }">
                <span :class="changeClass(row.score_change)">{{ formatChange(row.score_change) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="section">
          <div class="section-header">
            <div class="section-title"><span class="icon icon-blue">⚡</span>成绩波动 TOP 5</div>
            <span class="section-sub">按分数变化绝对值排序</span>
          </div>
          <el-table :data="dashboard.fluctuation" size="small" stripe>
            <el-table-column type="index" label="#" width="44">
              <template #default="{ $index }">
                <span style="font-weight: 600; color: var(--color-primary)">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="姓名" min-width="90">
              <template #default="{ row }">
                <div class="student-name">{{ row.student_name }}</div>
                <div class="student-id">{{ row.username }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="60">
              <template #default="{ row }">
                <span class="score-val">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="分数变化" width="100">
              <template #default="{ row }">
                <span :class="['change-tag', changeClass(row.score_change)]" style="font-weight: 700">
                  {{ formatChange(row.score_change) }}
                </span>
                <div class="sub-text">{{ row.prev_score }} → {{ row.score }}</div>
              </template>
            </el-table-column>
            <el-table-column label="名次变化" width="100">
              <template #default="{ row }">
                <span v-if="row.rank_change !== null" :class="['change-tag', changeClass(row.rank_change)]">
                  {{ row.rank_change > 0 ? '↑' : row.rank_change < 0 ? '↓' : '' }}{{ Math.abs(row.rank_change) }}
                </span>
                <span v-else class="sub-text">—</span>
                <div class="sub-text" v-if="row.prev_class_rank && row.class_rank">
                  {{ row.prev_class_rank }} → {{ row.class_rank }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 需关注学生 -->
      <div v-if="dashboard.needs_attention?.length" class="section">
        <div class="section-header">
          <div class="section-title"><span class="icon icon-red">!</span>需关注的学生</div>
          <span class="section-sub">连续两次考试{{ SUBJECTS[selectedSubject] }}成绩下降</span>
        </div>
        <el-table :data="dashboard.needs_attention" size="small" :row-class-name="() => 'attention-row'">
          <el-table-column label="姓名" min-width="80">
            <template #default="{ row }">
              <span class="student-name">{{ row.student_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="学号" width="100">
            <template #default="{ row }">
              <span class="student-id">{{ row.username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="class_name" label="班级" width="120" />
          <el-table-column label="本次" width="70">
            <template #default="{ row }">
              <span style="font-weight: 600; color: var(--color-danger)">{{ row.current_score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="prev_score" label="上次" width="70" />
          <el-table-column prop="prev_prev_score" label="上上次" width="70" />
          <el-table-column label="变化趋势" width="140">
            <template #default="{ row }">
              <div class="trend-cell">
                <div class="trend-spark">
                  <div class="trend-bar" :style="{ height: Math.min(Math.abs(row.trend[0]) * 1.5, 20) + 'px', background: '#FCA5A5' }"></div>
                  <div class="trend-bar" :style="{ height: Math.min(Math.abs(row.trend[1]) * 1.5, 20) + 'px', background: '#EF4444' }"></div>
                </div>
                <span class="trend-text">{{ row.trend[0] }} → {{ row.trend[1] }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- ════════════════════════════════════════ -->
    <!--          单班视图                        -->
    <!-- ════════════════════════════════════════ -->
    <div v-if="!isOverall && dashboard?.summary" class="view-content">
      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-label">平均分</div>
          <div class="stat-value">{{ dashboard.summary.avg_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最高分</div>
          <div class="stat-value">{{ dashboard.summary.max_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最低分</div>
          <div class="stat-value">{{ dashboard.summary.min_score }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">及格率</div>
          <div class="stat-value">{{ dashboard.summary.pass_rate }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">优秀率</div>
          <div class="stat-value">{{ dashboard.summary.excellent_rate }}<span class="unit">%</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">参考人数</div>
          <div class="stat-value">{{ dashboard.summary.total_students }}<span class="unit">人</span></div>
        </div>
      </div>

      <!-- 前十名 + 波动 -->
      <div class="two-col">
        <div class="section">
          <div class="section-header">
            <div class="section-title"><span class="icon icon-gold">★</span>班级前十名</div>
            <span class="section-sub">{{ currentClass?.name }} · {{ SUBJECTS[selectedSubject] }}</span>
          </div>
          <el-table :data="dashboard.top_students" size="small" stripe>
            <el-table-column type="index" label="#" width="44">
              <template #default="{ $index }">
                <span :class="['rank-badge', $index < 3 ? 'rank-top' : $index < 10 ? 'rank-mid' : '']">
                  {{ $index + 1 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="姓名" min-width="80">
              <template #default="{ row }">
                <span class="student-name">{{ row.student_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="学号" width="100">
              <template #default="{ row }">
                <span class="student-id">{{ row.username }}</span>
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="70">
              <template #default="{ row }">
                <span class="score-val">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="排名" width="60">
              <template #default="{ row }">
                <span :class="rankBadgeClass(row.class_rank)">{{ row.class_rank ?? '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="变化" width="120">
              <template #default="{ row }">
                <span v-if="row.rank_change !== null" :class="changeClass(row.rank_change)">↑{{ row.rank_change }}</span>
                <span v-if="row.score_change !== null" :class="['change-tag', changeClass(row.score_change)]" style="margin-left:4px">
                  {{ formatChange(row.score_change) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="section">
          <div class="section-header">
            <div class="section-title"><span class="icon icon-blue">⚡</span>成绩波动 TOP 5</div>
            <span class="section-sub">按分数变化绝对值排序</span>
          </div>
          <el-table :data="dashboard.fluctuation" size="small" stripe>
            <el-table-column type="index" label="#" width="44">
              <template #default="{ $index }">
                <span style="font-weight: 600; color: var(--color-primary)">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="姓名" min-width="90">
              <template #default="{ row }">
                <div class="student-name">{{ row.student_name }}</div>
                <div class="student-id">{{ row.username }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="60">
              <template #default="{ row }">
                <span class="score-val">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="分数变化" width="100">
              <template #default="{ row }">
                <span :class="['change-tag', changeClass(row.score_change)]" style="font-weight: 700">
                  {{ formatChange(row.score_change) }}
                </span>
                <div class="sub-text">{{ row.prev_score }} → {{ row.score }}</div>
              </template>
            </el-table-column>
            <el-table-column label="名次变化" width="100">
              <template #default="{ row }">
                <span v-if="row.rank_change !== null" :class="['change-tag', changeClass(row.rank_change)]">
                  {{ row.rank_change > 0 ? '↑' : row.rank_change < 0 ? '↓' : '' }}{{ Math.abs(row.rank_change) }}
                </span>
                <span v-else class="sub-text">—</span>
                <div class="sub-text" v-if="row.prev_class_rank && row.class_rank">
                  {{ row.prev_class_rank }} → {{ row.class_rank }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 需关注学生 -->
      <div v-if="dashboard.needs_attention?.length" class="section">
        <div class="section-header">
          <div class="section-title"><span class="icon icon-red">!</span>需关注的学生</div>
          <span class="section-sub">连续两次考试{{ SUBJECTS[selectedSubject] }}成绩下降</span>
        </div>
        <el-table :data="dashboard.needs_attention" size="small" :row-class-name="() => 'attention-row'">
          <el-table-column label="姓名" min-width="80">
            <template #default="{ row }">
              <span class="student-name">{{ row.student_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="学号" width="100">
            <template #default="{ row }">
              <span class="student-id">{{ row.username }}</span>
            </template>
          </el-table-column>
          <el-table-column label="本次" width="70">
            <template #default="{ row }">
              <span style="font-weight: 600; color: var(--color-danger)">{{ row.current_score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="prev_score" label="上次" width="70" />
          <el-table-column prop="prev_prev_score" label="上上次" width="70" />
          <el-table-column label="变化趋势" width="140">
            <template #default="{ row }">
              <div class="trend-cell">
                <div class="trend-spark">
                  <div class="trend-bar" :style="{ height: Math.min(Math.abs(row.trend[0]) * 1.5, 20) + 'px', background: '#FCA5A5' }"></div>
                  <div class="trend-bar" :style="{ height: Math.min(Math.abs(row.trend[1]) * 1.5, 20) + 'px', background: '#EF4444' }"></div>
                </div>
                <span class="trend-text">{{ row.trend[0] }} → {{ row.trend[1] }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 成绩编辑表格（仅单班视图） -->
      <div class="section">
        <div class="section-header">
          <div class="section-title">📝 成绩录入</div>
          <span class="section-sub">{{ currentClass?.name }} · {{ selectedExamName }} · {{ SUBJECTS[selectedSubject] }}</span>
        </div>
        <el-table :data="students" size="small" stripe max-height="460">
          <el-table-column type="index" label="#" width="44" />
          <el-table-column prop="username" label="学号" width="100">
            <template #default="{ row }">
              <span class="student-id">{{ row.username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="student_name" label="姓名" min-width="80">
            <template #default="{ row }">
              <span class="student-name">{{ row.student_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="成绩" width="130">
            <template #default="{ row }">
              <el-input-number
                :model-value="getScoreDisplay(row.student_id)"
                :min="0"
                :max="100"
                :precision="1"
                :step="0.5"
                controls-position="right"
                size="small"
                style="width: 110px"
                :placeholder="row.score !== null ? String(row.score) : '录入'"
                @update:model-value="(val: number | undefined) => { if (val !== undefined) editingScores[row.student_id] = val }"
              />
            </template>
          </el-table-column>
          <el-table-column label="班排" width="70">
            <template #default="{ row }">
              <span :class="rankBadgeClass(row.class_rank)">{{ row.class_rank ?? '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="校排" width="70">
            <template #default="{ row }">
              <span :class="rankBadgeClass(row.school_rank)">{{ row.school_rank ?? '—' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && (!dashboard || !dashboard.summary)" class="empty-state">
      <p v-if="!selectedExamName">请选择一次考试</p>
      <p v-else-if="!currentExamIds">该班级暂无此考试数据</p>
      <p v-else>暂无成绩数据</p>
    </div>

    <!-- ── 新建考试弹窗 ── -->
    <el-dialog v-model="showNewExamDialog" title="新建考试" width="400px">
      <el-form label-width="80px">
        <el-form-item label="考试名称">
          <el-input v-model="newExamName" placeholder="如：第一次月考" />
        </el-form-item>
        <el-form-item label="考试日期">
          <el-date-picker
            v-model="newExamDate"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item v-if="isOverall" label="所属班级">
          <span class="sub-text">将创建在{{ teacherClasses[0]?.name || '第一个班' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewExamDialog = false">取消</el-button>
        <el-button type="primary" @click="handleNewExam">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.scores-manage {
  padding: 8px 0;
}

/* ── 筛选栏 ── */
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.filter-item label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

/* ── 概览横幅 ── */
.overall-banner {
  background: linear-gradient(135deg, #EEF2FF, #F0F9FF);
  border: 1px solid #C7D2FE;
  border-radius: var(--radius-lg);
  padding: 16px 24px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.banner-label {
  font-size: 12px;
  color: var(--color-primary);
  font-weight: 500;
}
.banner-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary-dark);
}
.banner-unit {
  font-size: 14px;
  font-weight: 400;
}

/* ── 对比卡片 ── */
.compare-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.compare-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
  background: linear-gradient(135deg, #F8FAFC, #FFF);
}
.compare-card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.dot-a { background: var(--color-primary); }
.dot-b { background: var(--color-primary-light); }
.compare-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.compare-stat {
  display: flex;
  flex-direction: column;
}
.compare-stat .label {
  font-size: 11px;
  color: var(--color-text-light);
}
.compare-stat .val {
  font-size: 16px;
  font-weight: 600;
}

/* ── 统计卡片 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}
.stat-label {
  font-size: 11px;
  color: var(--color-text-light);
  margin-bottom: 2px;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}
.stat-value .unit {
  font-size: 13px;
  font-weight: 400;
  color: var(--color-text-secondary);
  margin-left: 2px;
}

/* ── 两列布局 ── */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
@media (max-width: 900px) {
  .two-col { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: repeat(3, 1fr); }
  .compare-row { grid-template-columns: 1fr; }
}

/* ── Section ── */
.section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-sub {
  font-size: 12px;
  color: var(--color-text-light);
}
.icon {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.icon-gold { background: #FEF3C7; color: #D97706; }
.icon-blue { background: #DBEAFE; color: #2563EB; }
.icon-red  { background: #FEE2E2; color: #DC2626; }

/* ── 表格内样式 ── */
.student-name { font-weight: 500; }
.student-id {
  color: var(--color-text-light);
  font-size: 12px;
  font-family: var(--font-mono);
}
.class-tag {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.score-val { font-weight: 600; }
.sub-text {
  font-size: 11px;
  color: var(--color-text-light);
  margin-top: 1px;
}

/* ── 排名徽章 ── */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}
.rank-top  { background: #D1FAE5; color: #065F46; }
.rank-mid  { background: #FEF3C7; color: #92400E; }
.rank-low  { background: #FEE2E2; color: #991B1B; }

/* ── 变化标签 ── */
.change-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}
.change-up   { color: #059669; background: #D1FAE5; }
.change-down { color: #DC2626; background: #FEE2E2; }
.change-flat { color: var(--color-text-light); }

/* ── 趋势条 ── */
.trend-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}
.trend-spark {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 20px;
}
.trend-bar {
  width: 8px;
  border-radius: 2px 2px 0 0;
  min-height: 4px;
}
.trend-text {
  font-size: 12px;
  color: var(--color-danger);
}

/* ── 需关注行 ── */
:deep(.attention-row) {
  background: #FFF7ED !important;
}
:deep(.attention-row:hover > td) {
  background: #FFF1E0 !important;
}

/* ── 空状态 ── */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--color-text-light);
  font-size: 14px;
}
</style>
