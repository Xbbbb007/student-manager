import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '../types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)

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
  }

  function logout() {
    setToken(null)
    setUserInfo(null)
  }

  return { token, userInfo, setToken, setUserInfo, logout }
})
