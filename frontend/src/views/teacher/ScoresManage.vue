<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import { listClassesApi } from '../../api/classes'
import { getExams, getClassScores, batchSaveScores, getClassStats, createExam } from '../../api/scores'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const userInfo = userStore.userInfo

// ─── 权限 ────────────────────────────────────
const isHomeroom = ref(false)
const teacherSubject = ref<string | null>(null)
const isAdmin = ref(false)

// ─── 数据 ────────────────────────────────────
interface ClassItem { id: number; name: string; section: string; grade: string }
interface ExamItem { id: number; name: string; class_id: number; exam_date: string }
interface StudentScore { student_id: number; student_name: string; username: string; score: number | null; class_rank: number | null; school_rank: number | null }
interface SubjectStats { avg_score: number; max_score: number; min_score: number; pass_rate: number; excellent_rate: number; pass_count: number; total_count: number; distribution: Record<string, number> }

const SUBJECTS: Record<string, string> = { chinese: '语文', math: '数学', english: '英语', science: '科学', ethics: '道德与法治' }
const SUBJECT_KEYS = Object.keys(SUBJECTS)

const classes = ref<ClassItem[]>([])
const exams = ref<ExamItem[]>([])
const students = ref<StudentScore[]>([])
const stats = ref<Record<string, SubjectStats>>({})
const editingScores = ref<Record<number, number>>({})

const selectedClassId = ref<number | null>(null)
const selectedExamId = ref<number | null>(null)
const selectedSubject = ref<string>('')

const loading = ref(false)
const saving = ref(false)
const showNewExamDialog = ref(false)
const newExamName = ref('')
const newExamDate = ref('')
const activeTab = ref('edit') // 'edit' | 'stats'

// ─── 计算属性 ────────────────────────────────
const filteredSubjects = computed(() => {
  // 管理员或班主任能看到所有科目
  if (isAdmin.value || isHomeroom.value) return SUBJECT_KEYS
  // 普通老师只能看到自己的科目
  if (teacherSubject.value && SUBJECT_KEYS.includes(teacherSubject.value)) {
    return [teacherSubject.value]
  }
  return SUBJECT_KEYS
})

const currentStats = computed(() => {
  if (!selectedSubject.value || !stats.value[selectedSubject.value]) return null
  return stats.value[selectedSubject.value]
})

const hasUnsavedChanges = computed(() => {
  return Object.keys(editingScores.value).length > 0
})

// ─── 方法 ────────────────────────────────────
async function loadClasses() {
  try {
    const res: any = await listClassesApi()
    classes.value = res.data || []
  } catch (e) {
    console.error('加载班级失败', e)
  }
}

async function loadExams() {
  if (!selectedClassId.value) { exams.value = []; return }
  try {
    const res: any = await getExams(selectedClassId.value)
    exams.value = res.data || []
  } catch {
    exams.value = []
  }
}

async function loadScores() {
  if (!selectedExamId.value || !selectedSubject.value) { students.value = []; return }
  loading.value = true
  try {
    const res: any = await getClassScores(selectedExamId.value, selectedSubject.value)
    students.value = res.data?.students || []
    editingScores.value = {}
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载成绩失败')
    students.value = []
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  if (!selectedExamId.value) { stats.value = {}; return }
  try {
    const res: any = await getClassStats(selectedExamId.value)
    stats.value = res.data?.stats || {}
  } catch {
    stats.value = {}
  }
}

function handleClassChange() {
  selectedExamId.value = null
  selectedSubject.value = ''
  students.value = []
  editingScores.value = {}
  loadExams()
}

function handleExamChange() {
  selectedSubject.value = ''
  students.value = []
  editingScores.value = {}
  if (selectedExamId.value) {
    loadStats()
  }
}

function handleSubjectChange() {
  loadScores()
}

function updateScore(studentId: number, value: string) {
  const score = parseFloat(value)
  if (isNaN(score) || score < 0) return
  if (score > 100) { ElMessage.warning('分数不能超过100'); return }
  editingScores.value[studentId] = score
}

async function saveScores() {
  const ids = Object.keys(editingScores.value)
  if (ids.length === 0) { ElMessage.info('没有需要保存的修改'); return }

  saving.value = true
  try {
    const items = ids.map(sid => ({
      student_id: parseInt(sid),
      exam_id: selectedExamId.value!,
      subject: selectedSubject.value,
      score: editingScores.value[parseInt(sid)]
    }))
    await batchSaveScores(items)
    ElMessage.success(`已保存 ${items.length} 条成绩`)
    editingScores.value = {}
    await loadScores()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleNewExam() {
  if (!newExamName.value) { ElMessage.warning('请输入考试名称'); return }
  if (!selectedClassId.value) { ElMessage.warning('请先选择班级'); return }
  try {
    await createExam({
      name: newExamName.value,
      class_id: selectedClassId.value,
      exam_date: newExamDate.value || undefined,
    })
    ElMessage.success('考试创建成功')
    showNewExamDialog.value = false
    newExamName.value = ''
    newExamDate.value = ''
    await loadExams()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '创建考试失败')
  }
}

function getScore(studentId: number): string {
  if (editingScores.value[studentId] !== undefined) return String(editingScores.value[studentId])
  const s = students.value.find(s => s.student_id === studentId)
  return s?.score !== null && s?.score !== undefined ? String(s.score) : ''
}

function getRankBadge(rank: number | null): string {
  if (!rank) return ''
  if (rank <= 10) return 'rank-top'
  if (rank <= 20) return 'rank-mid'
  return 'rank-low'
}

// ─── 初始化 ──────────────────────────────────
onMounted(async () => {
  // 判断权限
  isAdmin.value = userInfo?.role === 'admin'
  if (!isAdmin.value && userInfo?.subject) {
    teacherSubject.value = userInfo.subject
  }
  isHomeroom.value = !isAdmin.value // simplified - real check happens in backend

  await loadClasses()

  // 如果是老师，自动选中第一个班级
  if (classes.value.length > 0) {
    selectedClassId.value = classes.value[0].id
    await loadExams()
  }
})
</script>

<template>
  <div class="scores-manage">
    <div class="page-header">
      <h2>📊 成绩管理</h2>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="showNewExamDialog = true">+ 新建考试</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <label>班级</label>
        <el-select v-model="selectedClassId" placeholder="选择班级" @change="handleClassChange" style="width:200px">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>
      <div class="filter-item">
        <label>考试</label>
        <el-select v-model="selectedExamId" placeholder="选择考试" @change="handleExamChange" style="width:200px">
          <el-option v-for="e in exams" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
      </div>
      <div class="filter-item">
        <label>科目</label>
        <el-select v-model="selectedSubject" placeholder="选择科目" @change="handleSubjectChange" style="width:160px">
          <el-option v-for="k in filteredSubjects" :key="k" :label="SUBJECTS[k]" :value="k" />
        </el-select>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="currentStats" class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ currentStats.avg_score }}</div>
        <div class="stat-label">平均分</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ currentStats.max_score }}</div>
        <div class="stat-label">最高分</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ currentStats.min_score }}</div>
        <div class="stat-label">最低分</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" :class="currentStats.pass_rate >= 80 ? 'text-success' : 'text-warning'">
          {{ currentStats.pass_rate }}%
        </div>
        <div class="stat-label">及格率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value text-primary">{{ currentStats.excellent_rate }}%</div>
        <div class="stat-label">优秀率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ currentStats.total_count }}</div>
        <div class="stat-label">参考人数</div>
      </div>
    </div>

    <!-- 成绩编辑表格 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title" v-if="selectedExamId && selectedSubject">
          {{ exams.find(e => e.id === selectedExamId)?.name }} · {{ SUBJECTS[selectedSubject] }}
        </span>
        <span class="table-title" v-else>请选择考试和科目</span>
        <div class="table-actions">
          <el-button type="primary" :disabled="!hasUnsavedChanges" :loading="saving" @click="saveScores">
            💾 保存 ({{ Object.keys(editingScores).length }})
          </el-button>
        </div>
      </div>

      <el-table :data="students" v-loading="loading" stripe style="width:100%" max-height="480">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="username" label="学号" width="100" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column label="成绩" width="140">
          <template #default="{ row }">
            <el-input-number
              v-model="editingScores[row.student_id]"
              :min="0" :max="100" :precision="1"
              :step="0.5"
              controls-position="right"
              size="small"
              style="width:110px"
              :placeholder="row.score !== null ? String(row.score) : '录入'"
              @update:model-value="(val) => { if (val !== undefined) editingScores[row.student_id] = val }"
            />
          </template>
        </el-table-column>
        <el-table-column label="班排名" width="80">
          <template #default="{ row }">
            <span v-if="row.class_rank" :class="getRankBadge(row.class_rank)">{{ row.class_rank }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="年排名" width="80">
          <template #default="{ row }">
            <span v-if="row.school_rank" :class="getRankBadge(row.school_rank)">{{ row.school_rank }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建考试对话框 -->
    <el-dialog v-model="showNewExamDialog" title="新建考试" width="400px">
      <el-form label-width="80px">
        <el-form-item label="考试名称">
          <el-input v-model="newExamName" placeholder="如：第一次月考" />
        </el-form-item>
        <el-form-item label="考试日期">
          <el-date-picker v-model="newExamDate" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
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
  padding: 8px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
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

.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: 12px 20px;
  min-width: 100px;
  text-align: center;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}
.stat-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-light);
  margin-top: 4px;
}
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-primary { color: var(--color-primary); }

.table-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}
.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border-light);
}
.table-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
}

.rank-top { color: var(--color-success); font-weight: 700; }
.rank-mid { color: var(--color-warning); font-weight: 700; }
.rank-low { color: var(--color-danger); font-weight: 700; }
</style>
