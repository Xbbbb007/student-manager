<script setup lang="ts">
import { ref } from 'vue'
import { ElButton, ElInput, ElForm, ElFormItem, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  try {
    // TODO: 阶段 3 实现真实登录
    ElMessage.success('登录成功（演示）')
    userStore.setToken('demo-token')
    userStore.setUserInfo({
      id: 1,
      username: 'admin',
      name: '系统管理员',
      role: 'admin'
    })
    router.push('/admin')
  } catch {
    ElMessage.error('登录失败')
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">智慧学生管理系统</h1>
      <p class="login-subtitle">Smart Student Management System</p>
      <ElForm
        :model="form"
        label-width="0"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <ElFormItem>
          <ElInput
            v-model="form.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
          />
        </ElFormItem>
        <ElFormItem>
          <ElInput
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </ElFormItem>
        <ElFormItem>
          <ElButton
            type="primary"
            size="large"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </ElButton>
        </ElFormItem>
      </ElForm>
      <p class="login-hint">演示账号：admin / admin123</p>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 50%, var(--color-primary-light) 100%);
}

.login-card {
  width: 420px;
  padding: 48px 40px;
  background: var(--color-bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  text-align: center;
}

.login-title {
  font-size: var(--font-size-xxl);
  color: var(--color-primary);
  margin-bottom: 4px;
}

.login-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.login-form {
  text-align: left;
}

.login-btn {
  width: 100%;
}

.login-hint {
  margin-top: 16px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
</style>
