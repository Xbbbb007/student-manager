<script setup lang="ts">
import { ref } from 'vue'
import { ElButton, ElInput, ElForm, ElFormItem, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { loginApi, getMeApi } from '../api/auth'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    // 1. 登录获取 token
    const res = await loginApi(form.value)
    const token = res.data.access_token
    userStore.setToken(token)

    // 2. 获取用户信息
    const meRes = await getMeApi()
    userStore.setUserInfo(meRes.data)

    ElMessage.success('登录成功')

    // 3. 按角色跳转
    const role = meRes.data.role
    if (role === 'admin') router.push('/admin')
    else if (role === 'teacher') router.push('/teacher')
    else router.push('/student')
  } catch (e: any) {
    const msg = e?.response?.data?.detail || e?.message || '登录失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
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
            :disabled="loading"
          />
        </ElFormItem>
        <ElFormItem>
          <ElInput
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </ElFormItem>
        <ElFormItem>
          <ElButton
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
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
  background: var(--color-bg-content);
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
.login-form { text-align: left; }
.login-btn { width: 100%; }
.login-hint {
  margin-top: 16px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
</style>
