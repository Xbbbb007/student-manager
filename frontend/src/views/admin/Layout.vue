<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

interface NavItem {
  label: string
  route: string
}

const navItems = ref<NavItem[]>([
  { label: '用户管理', route: '/admin/users' },
  { label: '教务', route: '/admin/edu' },
  { label: '图书', route: '/admin/books' },
  { label: '后勤', route: '/admin/logistics' },
  { label: '数据', route: '/admin/data' },
  { label: '设置', route: '/admin/settings' }
])

const activeIndex = ref(0)

function handleSelect(index: number) {
  activeIndex.value = index
  router.push(navItems.value[index].route)
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout">
    <nav class="navbar">
      <div class="nav-inner">
        <div class="nav-logo">
          <span class="logo-text">智慧学生</span>
        </div>
        <div class="nav-links">
          <div
            v-for="(item, index) in navItems"
            :key="item.route"
            class="nav-item"
            :class="{ active: activeIndex === index }"
            @click="handleSelect(index)"
          >
            {{ item.label }}
          </div>
          <div class="active-bar" :style="{ left: calc(px - 24px) }" />
        </div>
        <div class="nav-user">
          <span class="user-name">{{ userStore.userInfo?.name || '管理员' }}</span>
          <el-button text type="primary" @click="handleLogout">退出</el-button>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; }
.navbar { height: var(--nav-height); background: var(--color-bg-white); border-bottom: 1px solid var(--color-border); box-shadow: var(--shadow-sm); position: sticky; top: 0; z-index: 100; }
.nav-inner { max-width: 1200px; margin: 0 auto; height: 100%; display: flex; align-items: center; padding: 0 var(--spacing-lg); }
.nav-logo { flex-shrink: 0; }
.logo-text { font-size: var(--font-size-lg); font-weight: 700; color: var(--color-primary); }
.nav-links { flex: 1; display: flex; justify-content: center; align-items: center; position: relative; height: 100%; gap: 4px; }
.nav-item { padding: 0 16px; height: 100%; display: flex; align-items: center; cursor: pointer; color: var(--color-text-secondary); transition: color 0.2s; user-select: none; font-size: var(--font-size-sm); }
.nav-item:hover { color: var(--color-primary); }
.nav-item.active { color: var(--color-primary); font-weight: 600; }
.active-bar { position: absolute; bottom: 0; width: 48px; height: 3px; background: var(--color-primary); border-radius: 2px 2px 0 0; transition: left 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.nav-user { display: flex; align-items: center; gap: var(--spacing-sm); flex-shrink: 0; }
.main-content { flex: 1; overflow-y: auto; padding: var(--spacing-lg); background: var(--color-bg); }
</style>
