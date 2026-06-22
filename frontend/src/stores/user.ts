import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '../types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))

  // 从 localStorage 恢复用户信息
  const saved = localStorage.getItem('userInfo')
  const userInfo = ref<UserInfo | null>(saved ? JSON.parse(saved) : null)

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUserInfo(info: UserInfo | null) {
    userInfo.value = info
    if (info) {
      localStorage.setItem('userInfo', JSON.stringify(info))
    } else {
      localStorage.removeItem('userInfo')
    }
  }

  function logout() {
    setToken(null)
    setUserInfo(null)
  }

  return { token, userInfo, setToken, setUserInfo, logout }
})
