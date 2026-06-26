<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

const captchaInput = ref('')
const captchaCanvas = ref<HTMLCanvasElement | null>(null)
const captchaAnswer = ref('')
const isMathMode = ref(false)
let clickCount = 0

function generateRandomChar() {
  const chars = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ'
  return chars.charAt(Math.floor(Math.random() * chars.length))
}

function getRandomColor(min: number, max: number) {
  const r = Math.floor(Math.random() * (max - min) + min)
  const g = Math.floor(Math.random() * (max - min) + min)
  const b = Math.floor(Math.random() * (max - min) + min)
  return `rgb(${r},${g},${b})`
}

function refreshCaptcha() {
  clickCount++
  if (clickCount === 1) {
    isMathMode.value = false
  } else {
    isMathMode.value = Math.random() < 0.5
  }

  const canvas = captchaCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 1. 清空并绘制背景
  ctx.fillStyle = '#f3f4f6'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  let displayText = ''
  if (isMathMode.value) {
    const isPlus = Math.random() < 0.5
    if (isPlus) {
      const num1 = Math.floor(Math.random() * 10) + 1
      const num2 = Math.floor(Math.random() * 10) + 1
      displayText = `${num1} + ${num2} = ?`
      captchaAnswer.value = (num1 + num2).toString()
    } else {
      const num1 = Math.floor(Math.random() * 12) + 6
      const num2 = Math.floor(Math.random() * 5) + 1
      displayText = `${num1} - ${num2} = ?`
      captchaAnswer.value = (num1 - num2).toString()
    }
  } else {
    let code = ''
    for (let i = 0; i < 4; i++) {
      code += generateRandomChar()
    }
    displayText = code
    captchaAnswer.value = code.toLowerCase()
  }

  // 2. 绘制噪点和干扰线
  for (let i = 0; i < 30; i++) {
    ctx.fillStyle = getRandomColor(150, 220)
    ctx.beginPath()
    ctx.arc(Math.random() * canvas.width, Math.random() * canvas.height, 1.5, 0, 2 * Math.PI)
    ctx.fill()
  }

  for (let i = 0; i < 3; i++) {
    ctx.strokeStyle = getRandomColor(120, 200)
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height)
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height)
    ctx.stroke()
  }

  // 3. 绘制文字
  ctx.textBaseline = 'middle'
  if (isMathMode.value) {
    ctx.font = 'bold 20px "Cascadia Code", monospace'
    ctx.fillStyle = '#334EAC'
    ctx.save()
    ctx.translate(canvas.width / 2, canvas.height / 2)
    ctx.rotate((Math.random() - 0.5) * 0.1)
    ctx.textAlign = 'center'
    ctx.fillText(displayText, 0, 0)
    ctx.restore()
  } else {
    ctx.font = 'bold 22px "Cascadia Code", monospace'
    const charWidth = canvas.width / 5
    for (let i = 0; i < displayText.length; i++) {
      ctx.save()
      const x = (i + 1) * charWidth - 5 + (Math.random() - 0.5) * 5
      const y = canvas.height / 2 + (Math.random() - 0.5) * 6
      ctx.translate(x, y)
      ctx.rotate((Math.random() - 0.5) * 0.4)
      ctx.fillStyle = getRandomColor(20, 100)
      ctx.fillText(displayText[i], -8, 0)
      ctx.restore()
    }
  }

  captchaInput.value = ''
}

onMounted(() => {
  refreshCaptcha()
})

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (!captchaInput.value.trim()) {
    ElMessage.warning('请输入验证码')
    return
  }

  const verified = isMathMode.value
    ? captchaInput.value.trim() === captchaAnswer.value
    : captchaInput.value.trim().toLowerCase() === captchaAnswer.value

  if (!verified) {
    ElMessage.error('验证码错误，请重新输入')
    refreshCaptcha()
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
    refreshCaptcha() // 登录失败也刷新验证码，增强安全性
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
          <div class="captcha-container">
            <ElInput
              v-model="captchaInput"
              placeholder="验证码"
              size="large"
              :disabled="loading"
              class="captcha-input"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-canvas-wrapper" @click="refreshCaptcha" title="点击刷新验证码">
              <canvas ref="captchaCanvas" width="120" height="40"></canvas>
            </div>
          </div>
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
.captcha-container {
  display: flex;
  gap: 12px;
  width: 100%;
}
.captcha-input {
  flex: 1;
}
.captcha-canvas-wrapper {
  width: 120px;
  height: 40px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  user-select: none;
  transition: border-color 0.2s;
}
.captcha-canvas-wrapper:hover {
  border-color: var(--color-primary-light);
}
.captcha-canvas-wrapper::after {
  content: "点击刷新";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 9px;
  padding: 1px 0;
  text-align: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.captcha-canvas-wrapper:hover::after {
  opacity: 1;
}
</style>
