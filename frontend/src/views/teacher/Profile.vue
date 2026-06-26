<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getUserProfileApi, getHomeroomStudentsApi, updateHomeroomStudentApi } from "../../api/users";
import { User, Edit, Key, Notebook } from "@element-plus/icons-vue";

interface TeacherProfile {
  id: number;
  username: string;
  name: string;
  role: string;
  gender: string | null;
  subject: string | null;
  homeroom_class_id: number | null;
  homeroom_class_name: string | null;
}

interface StudentRecord {
  id: number;
  username: string;
  name: string;
  gender: string | null;
  password_plain: string;
}

const profile = ref<TeacherProfile | null>(null);
const homeroomData = ref<{ class_id: number; class_name: string; students: StudentRecord[] } | null>(null);
const loading = ref(true);
const editDialogVisible = ref(false);
const editForm = ref({
  id: 0,
  name: "",
  gender: "",
  password: "",
});
const editLoading = ref(false);

const ROLE_MAP: Record<string, string> = {
  admin: "系统管理员",
  teacher: "任课教师",
};

const GENDER_MAP: Record<string, string> = {
  male: "男",
  female: "女",
};

const SUBJECT_MAP: Record<string, string> = {
  chinese: "语文",
  math: "数学",
  english: "英语",
  science: "科学",
  ethics: "道德与法治",
};

async function loadData() {
  loading.value = true;
  try {
    const profileRes = await getUserProfileApi();
    profile.value = profileRes.data;

    // If homeroom teacher, fetch class students
    if (profile.value?.homeroom_class_id) {
      const homeroomRes = await getHomeroomStudentsApi();
      homeroomData.value = homeroomRes.data;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("获取个人资料失败");
  } finally {
    loading.value = false;
  }
}

function openEditDialog(student: StudentRecord) {
  editForm.value = {
    id: student.id,
    name: student.name,
    gender: student.gender || "",
    password: "",
  };
  editDialogVisible.value = true;
}

async function handleUpdateStudent() {
  if (!editForm.value.name.trim()) {
    ElMessage.warning("姓名不能为空");
    return;
  }

  editLoading.value = true;
  try {
    await updateHomeroomStudentApi(editForm.value.id, {
      name: editForm.value.name,
      gender: editForm.value.gender || undefined,
      password: editForm.value.password || undefined,
    });
    ElMessage.success("修改学生信息成功");
    editDialogVisible.value = false;
    // Reload class list
    const homeroomRes = await getHomeroomStudentsApi();
    if (homeroomData.value) {
      homeroomData.value.students = homeroomRes.data.students;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("修改学生信息失败");
  } finally {
    editLoading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="teacher-profile-container" v-loading="loading">
    <div class="layout-grid" v-if="profile">
      <!-- 个人卡片 -->
      <div class="card-box info-card">
        <div class="profile-header-decor">
          <div class="avatar-circle">
            <el-icon class="avatar-icon"><User /></el-icon>
          </div>
          <h2 class="teacher-name">{{ profile.name }}</h2>
          <span class="role-badge">
            {{ profile.homeroom_class_id ? '班主任' : ROLE_MAP[profile.role] || '教职工' }}
          </span>
        </div>

        <div class="profile-details">
          <div class="info-item">
            <span class="info-label">工号 (用户名)</span>
            <span class="info-value">{{ profile.username }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">教师姓名</span>
            <span class="info-value">{{ profile.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">授课科目</span>
            <span class="info-value">{{ SUBJECT_MAP[profile.subject || ''] || '无' }}</span>
          </div>
          <div class="info-item" v-if="profile.homeroom_class_name">
            <span class="info-label">班主任管理班级</span>
            <span class="info-value text-primary font-bold">{{ profile.homeroom_class_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">性别</span>
            <span class="info-value">{{ GENDER_MAP[profile.gender || ''] || '未设置' }}</span>
          </div>
        </div>
      </div>

      <!-- 班主任管理学生面板 -->
      <div class="card-box students-card" v-if="profile.homeroom_class_id && homeroomData">
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Notebook /></el-icon>
            <h3>{{ homeroomData.class_name }} — 学生管理面板</h3>
          </div>
          <span class="student-count-tag">全班共 {{ homeroomData.students.length }} 人</span>
        </div>

        <div class="table-wrapper">
          <el-table :data="homeroomData.students" style="width: 100%" class="custom-table">
            <el-table-column prop="username" label="学号" width="120" />
            <el-table-column prop="name" label="姓名" min-width="120">
              <template #default="{ row }">
                <span class="student-name-val">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="gender" label="性别" width="80">
              <template #default="{ row }">
                {{ GENDER_MAP[row.gender || ''] || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="password_plain" label="当前密码" width="120" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small" 
                  plain 
                  :icon="Edit"
                  @click="openEditDialog(row)"
                >
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 编辑学生 Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      title="修改学生信息"
      width="460px"
      append-to-body
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="editForm" label-position="top">
        <el-form-item label="学生姓名" required>
          <el-input v-model="editForm.name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio-button value="male">男</el-radio-button>
            <el-radio-button value="female">女</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="重置密码 (留空则不修改)">
          <el-input 
            v-model="editForm.password" 
            placeholder="请输入新密码" 
            show-password
            :prefix-icon="Key"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="editLoading" @click="handleUpdateStudent">保存修改</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.teacher-profile-container {
  width: 100%;
  padding: 10px 0 30px;
}

.layout-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 900px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
}

.card-box {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.info-card {
  display: flex;
  flex-direction: column;
}

.profile-header-decor {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #ffffff;
}

.avatar-circle {
  width: 70px;
  height: 70px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.avatar-icon {
  font-size: 34px;
  color: #ffffff;
}

.teacher-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}

.role-badge {
  background: rgba(255, 255, 255, 0.15);
  font-size: 10px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  letter-spacing: 1px;
}

.profile-details {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.info-value {
  font-size: 13px;
  color: var(--color-text);
  font-weight: 700;
}

/* Students Card */
.students-card {
  min-height: 400px;
}

.card-header {
  padding: 16px 20px;
  background: rgba(8, 31, 92, 0.02);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: var(--color-primary);
}

.card-header h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.student-count-tag {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-secondary);
  background: var(--color-border-light);
  padding: 3px 8px;
  border-radius: 4px;
}

.table-wrapper {
  padding: 20px;
}

.student-name-val {
  font-weight: 700;
  color: var(--color-text);
}

/* Dialog Footer */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
