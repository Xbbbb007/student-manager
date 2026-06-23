<script setup lang="ts">
import { ref, provide, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import gsap from 'gsap'

const router = useRouter()
const userStore = useUserStore()

const navListRef = ref<HTMLElement | null>(null)

interface NavItem {
  label: string
  route: string
}

const navItems = ref<NavItem[]>([
  { label: '学习', route: '/student/learn' },
  { label: '生活', route: '/student/life' },
  { label: '我的', route: '/student/profile' }
])

const activeIndex = ref(0)

/* ── Module mode (学习子模块激活时替换导航栏) ── */
const moduleMode = ref(false)
const moduleActiveTab = ref('')
let onModuleTabChange: ((tab: string) => void) | null = null
let onBackToHome: (() => void) | null = null

interface ModuleTabItem {
  id: string
  label: string
}

const moduleTabItems: ModuleTabItem[] = [
  { id: 'scores', label: '成绩' },
  { id: 'homework', label: '作业' },
  { id: 'exams', label: '考试' },
  { id: 'mistakes', label: '错题本' },
  { id: 'schedule', label: '课表' },
]

function handleSelect(index: number) {
  // 在模块模式下点击主导航项 → 退出模块模式并跳转
  if (moduleMode.value) {
    if (onBackToHome) onBackToHome()
    moduleMode.value = false
    moduleActiveTab.value = ''
    activeIndex.value = index
    nextTick(() => {
      syncNavColors()
      nextTick(() => updateActiveIndicator())
    })
    router.push(navItems.value[index].route)
    return
  }

  if (index === activeIndex.value && !moduleMode.value) return

  activeIndex.value = index

  // GSAP 颜色动画
  const navLinks = navListRef.value?.querySelectorAll('.nav-item a')
  if (navLinks) {
    gsap.to(navLinks, { color: '#6B7280', duration: 0.15 })
    gsap.to(navLinks[index], { color: '#334EAC', duration: 0.15 })
  }

  // 滑动指示条跟随
  updateActiveIndicator()

  router.push(navItems.value[index].route)
}

function handleModuleSelect(tabId: string) {
  if (moduleActiveTab.value === tabId) return
  moduleActiveTab.value = tabId

  // 颜色更新（syncNavColors 会根据 moduleActiveTab 自动定位）
  syncNavColors()

  if (onModuleTabChange) onModuleTabChange(tabId)
}

function handleBackToHome() {
  if (onBackToHome) onBackToHome()
  // 延迟切换导航，等待 Learn.vue 的内容淡出动画完成
  setTimeout(() => {
    moduleMode.value = false
    moduleActiveTab.value = ''
    nextTick(() => {
      syncNavColors()
      nextTick(() => updateActiveIndicator())
    })
  }, 260)
}

/* ── 内部辅助函数 ── */

function updateActiveIndicator() {
  const navList = navListRef.value
  if (!navList || !navList.isConnected) return

  const activeTab = moduleMode.value ? moduleActiveTab.value : null
  const activeIdx = moduleMode.value
    ? moduleTabItems.findIndex(t => t.id === activeTab)
    : activeIndex.value

  const targetItem = navList.children[activeIdx] as HTMLElement
  if (!targetItem) return

  const listRect = navList.getBoundingClientRect()
  const itemRect = targetItem.getBoundingClientRect()

  gsap.to('.active-nav', {
    left: itemRect.left - listRect.left,
    width: itemRect.width,
    duration: 0.5,
    ease: 'elastic.out(1, 0.5)'
  })
}

function syncNavColors() {
  const navLinks = navListRef.value?.querySelectorAll('.nav-item a')
  if (!navLinks) return

  const activeIdx = moduleMode.value
    ? moduleTabItems.findIndex(t => t.id === moduleActiveTab.value)
    : activeIndex.value

  navLinks.forEach((link, i) => {
    gsap.set(link, { color: i === activeIdx ? '#334EAC' : '#6B7280' })
  })
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

/* ── Provide 给子组件（Learn.vue）使用 ── */
provide('enterModuleMode', (tab: string) => {
  moduleMode.value = true
  moduleActiveTab.value = tab
  if (onModuleTabChange) onModuleTabChange(tab)
  nextTick(() => {
    syncNavColors()
    // 等待模块导航 DOM 渲染完毕再定位指示条
    nextTick(() => updateActiveIndicator())
  })
})
provide('exitModuleMode', () => {
  moduleMode.value = false
  moduleActiveTab.value = ''
  nextTick(() => {
    syncNavColors()
    nextTick(() => updateActiveIndicator())
  })
})
provide('onModuleTabChange', (cb: (tab: string) => void) => {
  onModuleTabChange = cb
})
provide('onBackToHome', (cb: () => void) => {
  onBackToHome = cb
})
provide('onSelectModuleTab', (tabId: string) => {
  handleModuleSelect(tabId)
})

/* ── 指示条 + 颜色跟随 active tab ── */
watch([moduleActiveTab, moduleMode], () => {
  if (!moduleMode.value) return
  nextTick(() => {
    syncNavColors()
    updateActiveIndicator()
  })
})
</script>

<template>
  <div class="layout">
    <nav class="navbar">
      <div class="nav-inner">
        <div class="nav-logo">智慧学生</div>

        <!-- 模块模式下的返回按钮 -->
        <button v-if="moduleMode" class="nav-back" @click="handleBackToHome">← 首页</button>

        <div class="nav-center">
          <div class="nav-links-wrapper">
            <!-- 主导航 -->
            <ul v-if="!moduleMode" class="nav-links" ref="navListRef" key="main">
              <li
                v-for="(item, index) in navItems"
                :key="item.route"
                class="nav-item"
              >
                <a
                  :class="{ active: activeIndex === index }"
                  @click.prevent="handleSelect(index)"
                >{{ item.label }}</a>
              </li>
            </ul>
            <!-- 模块标签 -->
            <ul v-else class="nav-links" ref="navListRef" key="module">
              <li
                v-for="(item, index) in moduleTabItems"
                :key="item.id"
                class="nav-item"
              >
                <a
                  :class="{ active: moduleActiveTab === item.id }"
                  @click.prevent="handleModuleSelect(item.id)"
                >{{ item.label }}</a>
              </li>
            </ul>
            <!-- 滑动指示条：独立于 v-for，由 updateActiveIndicator() 定位 -->
            <div class="active-nav"></div>
          </div>
        </div>

        <div class="nav-user">
          <span>{{ userStore.userInfo?.name || '学生' }}</span>
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

.navbar {
  height: var(--nav-height);
  background: var(--color-bg-content);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  position: sticky; top: 0; z-index: 100;
}
.nav-inner {
  max-width: 1200px; margin: 0 auto; height: 100%;
  display: flex; align-items: center; padding: 0 var(--spacing-lg);
}
.nav-logo {
  font-size: var(--font-size-lg);
  font-weight: 700; color: var(--color-primary);
  flex-shrink: 0; letter-spacing: 1px;
}
.nav-back {
  font-size: 13px; font-weight: 500; color: var(--color-text-light);
  cursor: pointer; background: none; border: none; font-family: inherit;
  padding: 6px 14px 6px 0; margin-right: 8px; letter-spacing: 1px;
  border-right: 1px solid var(--color-border); transition: color 0.2s;
  flex-shrink: 0;
}
.nav-back:hover { color: var(--color-text); }
.nav-center { flex: 1; display: flex; justify-content: center; }
.nav-links-wrapper { position: relative; }
.nav-links { display: flex; list-style: none; gap: 2rem; align-items: center; }
.nav-item { position: relative; }
.nav-item a {
  text-decoration: none; color: var(--color-text-secondary);
  font-weight: 600; font-size: 15px; cursor: pointer;
  padding: 16px 0; display: inline-block;
  transition: color 0.2s;
}
.nav-item a:hover { color: var(--color-primary); }
.active-nav {
  position: absolute;
  height: 2px; background: var(--color-primary);
  border-radius: 2px;
  left: 0; bottom: 8px; width: 0;
  pointer-events: none;
}
.nav-user {
  display: flex; align-items: center; gap: var(--spacing-sm);
  flex-shrink: 0; font-size: 13px; color: var(--color-text);
}
.main-content {
  flex: 1; overflow-y: auto;
  background: var(--color-bg-white);
}
</style>
