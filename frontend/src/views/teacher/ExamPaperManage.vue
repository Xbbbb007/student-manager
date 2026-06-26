<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getQuestions, getPapers, createPaper, autoGeneratePaper } from "../../api/teaching";
import { Plus, Cpu, View } from "@element-plus/icons-vue";

interface Question {
  id: number;
  subject: string;
  question_type: string;
  question_desc: string;
  difficulty: string;
  answer?: string;
  explanation?: string;
  creator_name: string;
}

interface ExamPaper {
  id: number;
  title: string;
  subject: string;
  difficulty: string;
  questions: number[];
  creator_name: string;
  created_at: string;
}

const activeTab = ref<"list" | "question_bank">("list");
const papers = ref<ExamPaper[]>([]);
const questions = ref<Question[]>([]);
const loading = ref(false);

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const DIFFICULTY_MAP: Record<string, string> = {
  easy: "简单",
  medium: "中等",
  hard: "困难"
};

// Filter states
const filterSubject = ref("");
const filterDifficulty = ref("");

// Dialog states
const showManualDialog = ref(false);
const showAutoDialog = ref(false);
const showPaperPreviewDialog = ref(false);
const selectedPaperQuestions = ref<Question[]>([]);
const previewPaperTitle = ref("");

// Paper Creation Form
const manualForm = ref({
  title: "",
  subject: "chinese",
  difficulty: "medium",
  selectedQuestions: [] as number[],
});

const autoForm = ref({
  title: "",
  subject: "chinese",
  difficulty: "medium",
  count: 5,
});

async function loadPapers() {
  loading.value = true;
  try {
    const res: any = await getPapers();
    papers.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取试卷列表失败");
  } finally {
    loading.value = false;
  }
}

async function loadQuestions() {
  loading.value = true;
  try {
    const res: any = await getQuestions({
      subject: filterSubject.value || undefined,
      difficulty: filterDifficulty.value || undefined,
    });
    questions.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取题库失败");
  } finally {
    loading.value = false;
  }
}

async function handleCreatePaperManual() {
  if (!manualForm.value.title.trim()) {
    ElMessage.warning("请填写试卷标题");
    return;
  }
  if (manualForm.value.selectedQuestions.length === 0) {
    ElMessage.warning("请至少选择一道试题");
    return;
  }

  try {
    await createPaper({
      title: manualForm.value.title,
      subject: manualForm.value.subject,
      difficulty: manualForm.value.difficulty,
      questions: manualForm.value.selectedQuestions,
    });
    ElMessage.success("手动组卷成功！");
    showManualDialog.value = false;
    manualForm.value = { title: "", subject: "chinese", difficulty: "medium", selectedQuestions: [] };
    loadPapers();
  } catch (error) {
    console.error(error);
    ElMessage.error("组卷失败");
  }
}

async function handleCreatePaperAuto() {
  if (!autoForm.value.title.trim()) {
    ElMessage.warning("请填写试卷标题");
    return;
  }
  try {
    await autoGeneratePaper({
      title: autoForm.value.title,
      subject: autoForm.value.subject,
      difficulty: autoForm.value.difficulty,
      count: autoForm.value.count,
    });
    ElMessage.success("智能自动组卷成功！");
    showAutoDialog.value = false;
    autoForm.value = { title: "", subject: "chinese", difficulty: "medium", count: 5 };
    loadPapers();
  } catch (error) {
    console.error(error);
    ElMessage.error("自动组卷失败，可能题库中符合条件的题目不足");
  }
}

async function previewPaper(paper: ExamPaper) {
  previewPaperTitle.value = paper.title;
  try {
    const res: any = await getQuestions({ subject: paper.subject });
    const allQs: Question[] = res.data || [];
    selectedPaperQuestions.value = allQs.filter(q => paper.questions.includes(q.id));
    showPaperPreviewDialog.value = true;
  } catch (error) {
    console.error(error);
    ElMessage.error("获取试卷题目详情失败");
  }
}

function openManualBuild() {
  loadQuestions();
  showManualDialog.value = true;
}

onMounted(() => {
  loadPapers();
});
</script>

<template>
  <div class="exam-paper-manage" v-loading="loading">
    <div class="header-action-bar">
      <h2>出卷组卷系统</h2>
      <div class="action-btns">
        <el-button type="primary" :icon="Plus" @click="openManualBuild">手动组卷</el-button>
        <el-button type="success" :icon="Cpu" @click="showAutoDialog = true">智能自动组卷</el-button>
      </div>
    </div>

    <!-- Tab Buttons -->
    <div class="custom-tabs">
      <button :class="['tab-btn', { active: activeTab === 'list' }]" @click="activeTab = 'list'; loadPapers()">
        已生成试卷 ({{ papers.length }})
      </button>
      <button :class="['tab-btn', { active: activeTab === 'question_bank' }]" @click="activeTab = 'question_bank'; loadQuestions()">
        试题题库管理
      </button>
    </div>

    <!-- Papers List View -->
    <div v-if="activeTab === 'list'" class="tab-content">
      <el-empty description="暂无已生成试卷，请点击上方按钮组卷" v-if="papers.length === 0" />
      <div v-else class="papers-grid">
        <div v-for="p in papers" :key="p.id" class="paper-card">
          <div class="p-header">
            <span class="p-tag">{{ SUBJECTS[p.subject] || p.subject }}</span>
            <span class="p-diff" :class="p.difficulty">{{ DIFFICULTY_MAP[p.difficulty] }}</span>
          </div>
          <h3 class="p-title">{{ p.title }}</h3>
          <p class="p-meta">
            <span>题目数量: <strong>{{ p.questions.length }}</strong> 道</span>
            <span>组卷人: {{ p.creator_name }}</span>
          </p>
          <div class="p-footer">
            <span class="p-date">{{ p.created_at }}</span>
            <el-button size="small" type="primary" plain :icon="View" @click="previewPaper(p)">预览试卷</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Questions Bank View -->
    <div v-else class="tab-content">
      <div class="filters-bar">
        <div class="filter-group">
          <el-select v-model="filterSubject" placeholder="筛选学科" clearable @change="loadQuestions" style="width: 140px">
            <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
          </el-select>
          <el-select v-model="filterDifficulty" placeholder="筛选难度" clearable @change="loadQuestions" style="width: 120px">
            <el-option v-for="(val, key) in DIFFICULTY_MAP" :key="key" :label="val" :value="key" />
          </el-select>
        </div>
        <span>题库共计 <strong>{{ questions.length }}</strong> 道题</span>
      </div>

      <div class="question-list">
        <div v-for="q in questions" :key="q.id" class="question-card">
          <div class="q-header">
            <div class="q-left">
              <span class="q-badge">{{ SUBJECTS[q.subject] }}</span>
              <span class="q-diff" :class="q.difficulty">{{ DIFFICULTY_MAP[q.difficulty] }}</span>
              <span class="q-type">{{ q.question_type === 'single' ? '单选题' : q.question_type === 'multiple' ? '多选题' : q.question_type === 'blank' ? '填空题' : '简答题' }}</span>
            </div>
            <span class="q-creator">录入老师: {{ q.creator_name }}</span>
          </div>
          <div class="q-desc">{{ q.question_desc }}</div>
          <div v-if="q.answer" class="q-answer"><strong>正确答案:</strong> {{ q.answer }}</div>
        </div>
      </div>
    </div>

    <!-- Modal: 手动组卷 -->
    <el-dialog v-model="showManualDialog" title="手动组卷" width="720px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="试卷标题" required>
          <el-input v-model="manualForm.title" placeholder="如：三年级期末数学测试卷" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="学科" style="flex:1">
            <el-select v-model="manualForm.subject" style="width:100%" @change="loadQuestions">
              <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
            </el-select>
          </el-form-item>
          <el-form-item label="建议难度" style="flex:1">
            <el-select v-model="manualForm.difficulty" style="width:100%">
              <el-option v-for="(val, key) in DIFFICULTY_MAP" :key="key" :label="val" :value="key" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="请勾选要加入试卷的题目" required>
          <div class="manual-q-list">
            <el-checkbox-group v-model="manualForm.selectedQuestions">
              <div v-for="q in questions.filter(item => item.subject === manualForm.subject)" :key="q.id" class="mq-item">
                <el-checkbox :label="q.id">
                  <span class="mq-badge">{{ DIFFICULTY_MAP[q.difficulty] }}</span>
                  <span class="mq-desc">{{ q.question_desc.slice(0, 80) }}...</span>
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showManualDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePaperManual">生成试卷</el-button>
      </template>
    </el-dialog>

    <!-- Modal: 智能自动组卷 -->
    <el-dialog v-model="showAutoDialog" title="智能自动组卷" width="460px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="试卷标题" required>
          <el-input v-model="autoForm.title" placeholder="如：科学三年级模拟测试卷" />
        </el-form-item>
        <el-form-item label="试卷学科" required>
          <el-select v-model="autoForm.subject" style="width: 100%">
            <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
          </el-select>
        </el-form-item>
        <div class="form-row">
          <el-form-item label="试卷难度" required style="flex: 1">
            <el-select v-model="autoForm.difficulty" style="width: 100%">
              <el-option v-for="(val, key) in DIFFICULTY_MAP" :key="key" :label="val" :value="key" />
            </el-select>
          </el-form-item>
          <el-form-item label="题目数量" required style="flex: 1">
            <el-input-number v-model="autoForm.count" :min="1" :max="30" style="width: 100%" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showAutoDialog = false">取消</el-button>
        <el-button type="success" @click="handleCreatePaperAuto">自动生成</el-button>
      </template>
    </el-dialog>

    <!-- Modal: 试卷预览 -->
    <el-dialog v-model="showPaperPreviewDialog" :title="previewPaperTitle" width="680px" append-to-body>
      <div class="paper-preview-container">
        <div v-for="(q, index) in selectedPaperQuestions" :key="q.id" class="preview-q-item">
          <div class="pq-num">第 {{ index + 1 }} 题 ({{ DIFFICULTY_MAP[q.difficulty] }})</div>
          <div class="pq-desc">{{ q.question_desc }}</div>
          <div class="pq-answer" v-if="q.answer">参考答案: {{ q.answer }}</div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="showPaperPreviewDialog = false">确认关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.exam-paper-manage {
  width: 100%;
}
.header-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-action-bar h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary-dark);
}
.action-btns {
  display: flex;
  gap: 12px;
}

.custom-tabs {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid var(--color-border-light);
  margin-bottom: 20px;
  padding-bottom: 6px;
}
.tab-btn {
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 8px 16px;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}
.tab-btn.active {
  color: var(--color-primary);
}
.tab-btn.active::after {
  content: "";
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--color-primary);
}

/* Papers Grid */
.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.paper-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.25s;
}
.paper-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}
.p-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.p-tag {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-primary);
  background: rgba(51, 78, 172, 0.08);
  padding: 2px 8px;
  border-radius: 12px;
}
.p-diff {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}
.p-diff.easy { background: #ECFDF5; color: #047857; }
.p-diff.medium { background: #FFFBEB; color: #B45309; }
.p-diff.hard { background: #FDF2F8; color: #BE185D; }

.p-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.4;
  margin-bottom: 12px;
  text-align: left;
}
.p-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 14px;
}
.p-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px dashed var(--color-border-light);
  padding-top: 10px;
}
.p-date {
  font-size: 11px;
  color: var(--color-text-light);
}

/* Question bank */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.filter-group {
  display: flex;
  gap: 12px;
}
.question-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.question-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  padding: 16px;
  text-align: left;
}
.q-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.q-left {
  display: flex;
  gap: 8px;
  align-items: center;
}
.q-badge {
  font-size: 10px;
  font-weight: 700;
  background: #f0f2f5;
  color: #555;
  padding: 1px 6px;
  border-radius: 10px;
}
.q-diff {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
}
.q-diff.easy { background: #e6f7ff; color: #1890ff; }
.q-diff.medium { background: #fff7e6; color: #fa8c16; }
.q-diff.hard { background: #fff0f6; color: #eb2f96; }
.q-type {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.q-creator {
  font-size: 11px;
  color: var(--color-text-light);
}
.q-desc {
  font-size: 14px;
  color: var(--color-text);
  line-height: 1.5;
  margin-bottom: 8px;
  white-space: pre-wrap;
}
.q-answer {
  font-size: 12px;
  color: var(--color-success);
}

/* Manual Build List */
.manual-q-list {
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  max-height: 280px;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mq-item {
  padding: 8px;
  border-bottom: 1px dashed var(--color-border-light);
}
.mq-item:last-child { border-bottom: none; }
.mq-badge {
  font-size: 10px;
  background: #f5f5f5;
  color: #666;
  padding: 1px 4px;
  border-radius: 3px;
  margin-right: 6px;
}
.mq-desc {
  font-size: 13px;
}
.form-row {
  display: flex;
  gap: 16px;
}

/* Paper Preview */
.paper-preview-container {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.preview-q-item {
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 14px;
  text-align: left;
}
.preview-q-item:last-child { border-bottom: none; }
.pq-num {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 6px;
}
.pq-desc {
  font-size: 14px;
  color: var(--color-text);
  line-height: 1.5;
  margin-bottom: 8px;
  white-space: pre-wrap;
}
.pq-answer {
  font-size: 12px;
  color: var(--color-success);
}
</style>
