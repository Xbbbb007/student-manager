<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getResources, uploadResource } from "../../api/teaching";
import { FolderOpened, UploadFilled, Search, Download } from "@element-plus/icons-vue";

interface ResourceItem {
  id: number;
  title: string;
  subject: string;
  grade: string;
  file_name: string;
  file_path: string;
  uploader_name: string;
  created_at: string;
}

const resources = ref<ResourceItem[]>([]);
const loading = ref(false);

const SUBJECTS: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

const GRADES = ["三年级", "四年级", "五年级", "六年级"];

// Filters
const filterSubject = ref("");
const filterGrade = ref("");
const searchKeyword = ref("");

// Upload Dialog
const showUploadDialog = ref(false);
const uploadLoading = ref(false);
const form = ref({
  title: "",
  subject: "chinese",
  grade: "三年级",
  file_name: "",
  file_path: ""
});

async function loadResources() {
  loading.value = true;
  try {
    const res: any = await getResources({
      subject: filterSubject.value || undefined,
      grade: filterGrade.value || undefined,
    });
    resources.value = res.data || [];
  } catch (error) {
    console.error(error);
    ElMessage.error("获取教学资源列表失败");
  } finally {
    loading.value = false;
  }
}

async function handleUpload() {
  if (!form.value.title.trim()) {
    ElMessage.warning("请填写资源标题");
    return;
  }
  if (!form.value.file_name.trim()) {
    ElMessage.warning("请指定模拟上传的文件名");
    return;
  }

  // Simulate file path
  form.value.file_path = `/static/uploads/${form.value.file_name}`;

  uploadLoading.value = true;
  try {
    await uploadResource(form.value);
    ElMessage.success("教学资源上传/发布成功！");
    showUploadDialog.value = false;
    form.value = { title: "", subject: "chinese", grade: "三年级", file_name: "", file_path: "" };
    loadResources();
  } catch (error) {
    console.error(error);
    ElMessage.error("资源发布失败");
  } finally {
    uploadLoading.value = false;
  }
}

function triggerDownload(item: ResourceItem) {
  ElMessage.success(`正在下载资源: ${item.file_name} (模拟下载)`);
}

onMounted(() => {
  loadResources();
});
</script>

<template>
  <div class="resource-library" v-loading="loading">
    <div class="header-action-bar">
      <h2>共享教案课件资源库</h2>
      <el-button type="primary" :icon="UploadFilled" @click="showUploadDialog = true">发布新课件资源</el-button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <el-select v-model="filterSubject" placeholder="学科筛选" clearable @change="loadResources" style="width: 140px">
          <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
        </el-select>
        <el-select v-model="filterGrade" placeholder="年级筛选" clearable @change="loadResources" style="width: 140px">
          <el-option v-for="g in GRADES" :key="g" :label="g" :value="g" />
        </el-select>
      </div>
      <div class="search-box">
        <el-input v-model="searchKeyword" placeholder="搜素课件资源名称..." :prefix-icon="Search" clearable />
      </div>
    </div>

    <!-- Grid List -->
    <el-empty description="此筛选条件暂无教学课件资源，请点击上方按钮发布" v-if="resources.length === 0" />
    <div v-else class="resources-grid">
      <div 
        v-for="r in resources.filter(item => !searchKeyword || item.title.toLowerCase().includes(searchKeyword.toLowerCase()))" 
        :key="r.id" 
        class="resource-card"
      >
        <div class="rc-header">
          <span class="subject-tag">{{ SUBJECTS[r.subject] || r.subject }}</span>
          <span class="grade-tag">{{ r.grade }}</span>
        </div>
        
        <div class="rc-body">
          <el-icon class="file-icon"><FolderOpened /></el-icon>
          <div class="file-info">
            <h4 class="file-title" :title="r.title">{{ r.title }}</h4>
            <p class="file-meta-name">{{ r.file_name }}</p>
          </div>
        </div>

        <div class="rc-footer">
          <div class="uploader-info">
            <span class="uploader">{{ r.uploader_name }}</span>
            <span class="date">{{ r.created_at.split(' ')[0] }}</span>
          </div>
          <el-button size="small" type="primary" plain :icon="Download" @click="triggerDownload(r)">下载</el-button>
        </div>
      </div>
    </div>

    <!-- Modal: Upload Resource -->
    <el-dialog v-model="showUploadDialog" title="发布新教学课件资源" width="460px" destroy-on-close append-to-body>
      <el-form label-position="top">
        <el-form-item label="资源/课件标题" required>
          <el-input v-model="form.title" placeholder="如：三年级下册语文《静夜思》多媒体课件" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="学科" required style="flex: 1">
            <el-select v-model="form.subject" style="width: 100%">
              <el-option v-for="(val, key) in SUBJECTS" :key="key" :label="val" :value="key" />
            </el-select>
          </el-form-item>
          <el-form-item label="适用年级" required style="flex: 1">
            <el-select v-model="form.grade" style="width: 100%">
              <el-option v-for="g in GRADES" :key="g" :label="g" :value="g" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="上传课件文件名 (模拟上传)" required>
          <el-input v-model="form.file_name" placeholder="请输入文件名，如：lesson1_ppt.pdf" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploadLoading" @click="handleUpload">发布上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resource-library {
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

.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.filter-group {
  display: flex;
  gap: 12px;
}
.search-box {
  width: 260px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.resource-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.25s;
}
.resource-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.rc-header {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}
.subject-tag {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-primary);
  background: rgba(51, 78, 172, 0.08);
  padding: 1px 8px;
  border-radius: 12px;
}
.grade-tag {
  font-size: 10px;
  font-weight: 700;
  color: #319795;
  background: #e6fffa;
  padding: 1px 8px;
  border-radius: 12px;
}

.rc-body {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  text-align: left;
}
.file-icon {
  font-size: 36px;
  color: #dd6b20;
  flex-shrink: 0;
}
.file-info {
  min-width: 0;
  flex: 1;
}
.file-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-meta-name {
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-light);
  padding-top: 12px;
}
.uploader-info {
  display: flex;
  flex-direction: column;
  font-size: 11px;
  color: var(--color-text-light);
  text-align: left;
}
.uploader {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.form-row {
  display: flex;
  gap: 16px;
}
</style>
