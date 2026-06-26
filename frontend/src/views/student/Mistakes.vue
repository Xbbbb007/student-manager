<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getMyMistakes, addMistake, toggleMistakeMastered, getMistakeStats } from "../../api/mistake";
import { Plus, CircleCheck, Medal, Warning, ArrowDown, ArrowUp } from "@element-plus/icons-vue";

interface MistakeItem {
  id: number;
  subject: string;
  subject_name: string;
  question_desc: string;
  my_answer: string | null;
  correct_answer: string | null;
  is_mastered: boolean;
  created_at: string;
  show_details?: boolean;  // local state
}

interface SubjectStat {
  subject: string;
  subject_name: string;
  count: number;
  mastered_count: number;
}

interface StatsData {
  total: number;
  mastered: number;
  active: number;
  mastered_rate: number;
  by_subject: SubjectStat[];
}

const mistakes = ref<MistakeItem[]>([]);
const stats = ref<StatsData>({
  total: 0,
  mastered: 0,
  active: 0,
  mastered_rate: 0,
  by_subject: [],
});
const loading = ref(true);
const activeTab = ref<"active" | "mastered">("active");

const showAddDialog = ref(false);
const addLoading = ref(false);
const form = ref({
  subject: "chinese",
  question_desc: "",
  my_answer: "",
  correct_answer: "",
});

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

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

async function loadData() {
  loading.value = true;
  try {
    const isMasteredParam = activeTab.value === "mastered";
    const [listRes, statsRes]: any = await Promise.all([
      getMyMistakes({ is_mastered: isMasteredParam }),
      getMistakeStats(),
    ]);
    mistakes.value = (listRes.data || []).map((m: any) => ({ ...m, show_details: false }));
    stats.value = statsRes.data || { total: 0, mastered: 0, active: 0, mastered_rate: 0, by_subject: [] };
  } catch (error) {
    console.error(error);
    ElMessage.error("获取错题本数据失败");
  } finally {
    loading.value = false;
  }
}

async function handleAddMistake() {
  if (!form.value.question_desc.trim()) {
    ElMessage.warning("请填写题目描述");
    return;
  }

  addLoading.value = true;
  try {
    await addMistake(form.value);
    ElMessage.success("错题添加成功！已放入待复习区");
    showAddDialog.value = false;
    form.value = {
      subject: "chinese",
      question_desc: "",
      my_answer: "",
      correct_answer: "",
    };
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("添加错题失败");
  } finally {
    addLoading.value = false;
  }
}

async function handleToggleMaster(item: MistakeItem) {
  try {
    const res: any = await toggleMistakeMastered(item.id);
    const newStatus = res.data?.is_mastered;
    ElMessage.success(newStatus ? "标记掌握！已移入已掌握区" : "已移回待复习区");
    loadData();
  } catch (error) {
    console.error(error);
    ElMessage.error("操作失败");
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="mistakes-container" v-loading="loading">
    <!-- 错题数据看板 -->
    <div class="stats-overview">
      <div class="stat-card active-cnt">
        <div class="stat-icon"><Warning /></div>
        <div class="stat-info">
          <span class="stat-label">待复习错题</span>
          <span class="stat-value">{{ stats.active }} <small>道</small></span>
        </div>
      </div>
      <div class="stat-card mastered-cnt">
        <div class="stat-icon"><CircleCheck /></div>
        <div class="stat-info">
          <span class="stat-label">已掌握错题</span>
          <span class="stat-value">{{ stats.mastered }} <small>道</small></span>
        </div>
      </div>
      <div class="stat-card rate-cnt">
        <div class="stat-icon"><Medal /></div>
        <div class="stat-info">
          <span class="stat-label">错题掌握率</span>
          <div class="rate-progress-wrapper">
            <span class="stat-value">{{ stats.mastered_rate }}%</span>
            <el-progress 
              :percentage="stats.mastered_rate" 
              :show-text="false" 
              status="success" 
              style="width: 80px"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 过滤器与发布按钮 -->
    <div class="filter-actions-bar">
      <div class="custom-tabs">
        <button 
          :class="['tab-item', { active: activeTab === 'active' }]"
          @click="activeTab = 'active'; loadData()"
        >
          待复习 ({{ stats.active }})
        </button>
        <button 
          :class="['tab-item', { active: activeTab === 'mastered' }]"
          @click="activeTab = 'mastered'; loadData()"
        >
          已掌握 ({{ stats.mastered }})
        </button>
      </div>
      <el-button type="primary" :icon="Plus" @click="showAddDialog = true">录入错题</el-button>
    </div>

    <!-- 列表展示 -->
    <div v-if="mistakes.length === 0" class="empty-state">
      <el-empty description="此区域暂无错题记录" />
    </div>

    <div v-else class="mistake-list">
      <div 
        v-for="m in mistakes" 
        :key="m.id"
        class="mistake-card"
      >
        <div class="mcard-header">
          <div class="mcard-left">
            <span 
              class="subject-tag"
              :style="{
                backgroundColor: getSubjectStyle(m.subject).bg,
                border: `1px solid ${getSubjectStyle(m.subject).border}`,
                color: getSubjectStyle(m.subject).text
              }"
            >
              {{ m.subject_name }}
            </span>
            <span class="mcard-date">{{ formatDate(m.created_at) }}</span>
          </div>
          
          <el-button 
            :type="m.is_mastered ? 'info' : 'success'" 
            size="small" 
            plain 
            :icon="CircleCheck"
            @click="handleToggleMaster(m)"
          >
            {{ m.is_mastered ? '移回待复习' : '标记掌握' }}
          </el-button>
        </div>

        <div class="question-text">
          {{ m.question_desc }}
        </div>

        <!-- 展开折叠区 -->
        <div class="expand-action" @click="m.show_details = !m.show_details">
          <span>{{ m.show_details ? '收起解析与作答' : '展开查看解析与作答' }}</span>
          <el-icon v-if="m.show_details"><ArrowUp /></el-icon>
          <el-icon v-else><ArrowDown /></el-icon>
        </div>

        <div class="expanded-answers" v-if="m.show_details">
          <div class="answer-block my">
            <div class="lbl">我的错解：</div>
            <div class="txt">{{ m.my_answer || '未填写。' }}</div>
          </div>
          <div class="answer-block correct">
            <div class="lbl">正确答案/解析：</div>
            <div class="txt">{{ m.correct_answer || '未填写。' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 录入错题 Dialog -->
    <el-dialog
      v-model="showAddDialog"
      title="录入新错题"
      width="540px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="学科" required>
          <el-select v-model="form.subject" placeholder="请选择错题学科" style="width: 100%">
            <el-option 
              v-for="(val, key) in SUBJECTS" 
              :key="key" 
              :label="val" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="错题题目描述" required>
          <el-input 
            v-model="form.question_desc" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入题目描述或问题信息..." 
          />
        </el-form-item>
        <el-form-item label="我的错误解答">
          <el-input 
            v-model="form.my_answer" 
            type="textarea" 
            :rows="3" 
            placeholder="选填，写下自己当时的解答，方便总结复习" 
          />
        </el-form-item>
        <el-form-item label="正确答案与分析步骤">
          <el-input 
            v-model="form.correct_answer" 
            type="textarea" 
            :rows="3" 
            placeholder="选填，写下正确步骤或解题思路" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" :loading="addLoading" @click="handleAddMistake">确认录入</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.mistakes-container {
  width: 100%;
}

/* 看板 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.stat-card.mastered-cnt .stat-icon {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
.stat-card.rate-cnt .stat-icon {
  background: rgba(51, 78, 172, 0.1);
  color: var(--color-primary);
}
.stat-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
}
.stat-value small {
  font-size: 12px;
  font-weight: normal;
  color: var(--color-text-secondary);
}

.rate-progress-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 控制条 */
.filter-actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 12px;
}
.custom-tabs {
  display: flex;
  gap: 8px;
}
.tab-item {
  background: transparent;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.25s;
}
.tab-item:hover {
  color: var(--color-primary);
  background: var(--color-border-light);
}
.tab-item.active {
  background: var(--color-primary);
  color: #ffffff;
}

/* 错题列表 */
.mistake-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.mistake-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}
.mistake-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
}

.mcard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.mcard-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.subject-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 12px;
  letter-spacing: 0.5px;
}
.mcard-date {
  font-size: 12px;
  color: var(--color-text-light);
}

.question-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text);
  margin-bottom: 14px;
  white-space: pre-wrap;
}

.expand-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  cursor: pointer;
  margin-bottom: 8px;
  transition: color 0.2s;
}
.expand-action:hover {
  color: var(--color-primary-light);
}

.expanded-answers {
  background: rgba(8, 31, 92, 0.015);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}
.answer-block .lbl {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.answer-block .txt {
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text);
  white-space: pre-wrap;
}
.answer-block.my .txt {
  color: var(--color-danger);
}
.answer-block.correct .txt {
  color: var(--color-success);
}

.empty-state {
  padding: 60px 0;
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
}

/* Dialog Form */
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
