<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getUserProfileApi } from "../../api/users";
import { User, InfoFilled } from "@element-plus/icons-vue";

interface StudentProfile {
  id: number;
  username: string;
  name: string;
  gender: string | null;
  class_id: number | null;
  class_name: string;
}

const profile = ref<StudentProfile | null>(null);
const loading = ref(true);

const GENDER_MAP: Record<string, string> = {
  male: "男",
  female: "女",
};

async function loadProfile() {
  loading.value = true;
  try {
    const res = await getUserProfileApi();
    profile.value = res.data;
  } catch (error) {
    console.error(error);
    ElMessage.error("获取个人信息失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="student-profile-container" v-loading="loading">
    <div class="profile-card" v-if="profile">
      <!-- 头部装饰 -->
      <div class="profile-header-decor">
        <div class="avatar-circle">
          <el-icon class="avatar-icon"><User /></el-icon>
        </div>
        <h2 class="student-name">{{ profile.name }}</h2>
        <span class="role-badge">学 生</span>
      </div>

      <!-- 信息表单区 -->
      <div class="profile-details">
        <div class="info-item">
          <span class="info-label">学号 (用户名)</span>
          <span class="info-value">{{ profile.username }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">姓名</span>
          <span class="info-value">{{ profile.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">所在班级</span>
          <span class="info-value">{{ profile.class_name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">性别</span>
          <span class="info-value">{{ GENDER_MAP[profile.gender || ''] || '未设置' }}</span>
        </div>
      </div>

      <!-- 安全提示 -->
      <div class="security-notice">
        <el-icon class="notice-icon"><InfoFilled /></el-icon>
        <div class="notice-text">
          学生个人基本信息为只读状态。如需修改姓名、性别等信息或重置密码，请联系您的班主任老师或系统管理员进行处理。
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.student-profile-container {
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
  padding: 20px 0 40px;
}

.profile-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.profile-header-decor {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  padding: 40px 20px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #ffffff;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.avatar-icon {
  font-size: 40px;
  color: #ffffff;
}

.student-name {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 1px;
}

.role-badge {
  background: rgba(255, 255, 255, 0.15);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
  letter-spacing: 2px;
}

.profile-details {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.info-value {
  font-size: 14px;
  color: var(--color-text);
  font-weight: 700;
}

.security-notice {
  margin: 10px 30px 30px;
  padding: 16px;
  background: rgba(51, 78, 172, 0.04);
  border: 1px solid rgba(51, 78, 172, 0.1);
  border-radius: 8px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.notice-icon {
  color: var(--color-primary);
  font-size: 18px;
  margin-top: 2px;
  flex-shrink: 0;
}

.notice-text {
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}
</style>
