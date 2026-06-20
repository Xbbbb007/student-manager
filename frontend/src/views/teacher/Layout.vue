<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import gsap from 'gsap'
import { Flip } from 'gsap/Flip'

gsap.registerPlugin(Flip)

const router = useRouter()
const userStore = useUserStore()
const navListRef = ref<HTMLElement | null>(null)

interface NavItem { label: string; route: string }
const navItems = ref<NavItem[]>([
  { label: '教学', route: '/teacher/teach' },
  { label: '管理', route: '/teacher/manage' },
  { label: '我的', route: '/teacher/profile' }
])
const activeIndex = ref(0)

function handleSelect(index: number) {
  if (index === activeIndex.value) return
  activeIndex.value = index
  
  const navLinks = navListRef.value?.querySelectorAll('.nav-item a')
  if (navLinks) {
    gsap.to(navLinks, { color: '#6B7280', duration: 0.15 })
    gsap.to(navLinks[index], { color: '#334EAC', duration: 0.15 })
  }
  const activeNav = navListRef.value?.querySelector('.active-nav')
  const targetItem = navListRef.value?.children[index] as HTMLElement
  if (activeNav && targetItem) {
    const state = Flip.getState(activeNav)
    targetItem.appendChild(activeNav)
    Flip.from(state, { duration: 0.6, ease: 'elastic.out(1, 0.5)', absolute: true })
  }
  router.push(navItems.value[index].route)
}

function handleLogout() { userStore.logout(); router.push('/login') }
</script>

<template>
  <div class="layout">
    <nav class="navbar">
      <div class="nav-inner">
        <div class="nav-logo">智慧学生</div>
        <div class="nav-center">
          <ul class="nav-links" ref="navListRef">
            <li v-for="(item, index) in navItems" :key="item.route" class="nav-item">
              <a :class="{ active: activeIndex === index }" @click.prevent="handleSelect(index)">{{ item.label }}</a>
              <div v-if="index === 0" class="active-nav"></div>
            </li>
          </ul>
        </div>
        <div class="nav-user">
          <span>{{ userStore.userInfo?.name || '教师' }}</span>
          <el-button text type="primary" @click="handleLogout">退出</el-button>
        </div>
      </div>
    </nav>
    <main class="main-content"><router-view /></main>
  </div>
</template>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; }
.navbar { height: var(--nav-height); background: var(--color-bg-content); border-bottom: 1px solid var(--color-border); box-shadow: var(--shadow-sm); position: sticky; top: 0; z-index: 100; }
.nav-inner { max-width: 1200px; margin: 0 auto; height: 100%; display: flex; align-items: center; padding: 0 var(--spacing-lg); }
.nav-logo { font-size: var(--font-size-lg); font-weight: 700; color: var(--color-primary); flex-shrink: 0; letter-spacing: 1px; }
.nav-center { flex: 1; display: flex; justify-content: center; }
.nav-links { display: flex; list-style: none; gap: 2rem; align-items: center; }
.nav-item { position: relative; }
.nav-item a { text-decoration: none; color: var(--color-text-secondary); font-weight: 600; font-size: 15px; cursor: pointer; padding: 16px 0; display: inline-block; transition: color 0.2s; }
.nav-item a:hover { color: var(--color-primary); }
.active-nav { position: absolute; height: 3px; background: var(--color-primary); border-radius: 2px; left: 0; bottom: -4px; width: 100%; }
.nav-user { display: flex; align-items: center; gap: var(--spacing-sm); flex-shrink: 0; font-size: 13px; color: var(--color-text); }
.main-content { flex: 1; overflow-y: auto; padding: var(--spacing-lg); background: var(--color-bg); }
</style>
