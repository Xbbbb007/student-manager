<script setup lang="ts">
import { ref, inject, onMounted, nextTick } from "vue"
import gsap from "gsap"
import Scores from "./Scores.vue"

const activeTab = ref("")
const quoteVisible = ref(true)
const isFlipped = ref(false)
const isEntered = ref(false)
const detailHTML = ref("")

const enterModuleMode = inject<(tab: string) => void>('enterModuleMode', () => {})

const registerModuleTabChange = inject<(cb: (tab: string) => void) => void>('onModuleTabChange', () => {})
const registerBackToHome = inject<(cb: () => void) => void>('onBackToHome', () => {})

const currentQuote = ref({
  text: "书籍是人类进步的阶梯",
  author: "高尔基",
  era: "苏联作家",
  desc: "玛克西姆·高尔基（1868—1936），苏联无产阶级作家，社会主义现实主义文学的奠基人。"
})

const quotes = [
  { text: "书籍是人类进步的阶梯", author: "高尔基", era: "苏联作家", desc: "玛克西姆·高尔基（1868—1936），苏联无产阶级作家，社会主义现实主义文学的奠基人。" },
  { text: "学而不思则罔<br>思而不学则殆", author: "孔子", era: "春秋时期思想家", desc: "孔子（前551—前479），名丘，字仲尼，儒家学派创始人，中国古代伟大的思想家、教育家。" },
  { text: "知识就是力量", author: "培根", era: "英国哲学家", desc: "弗朗西斯·培根（1561—1626），英国文艺复兴时期散文家、哲学家，近代归纳法创始人。" },
  { text: "教育不是填满一桶水<br>而是点燃一把火", author: "叶芝", era: "爱尔兰诗人", desc: "威廉·巴特勒·叶芝（1865—1939），爱尔兰诗人、剧作家，1923年诺贝尔文学奖得主。" },
]

function pickRandom() {
  const q = quotes[Math.floor(Math.random() * quotes.length)]
  currentQuote.value = q
  isFlipped.value = false
}

const tabData: Record<string, string> = {
  scores: `<p class="detail-title">各科成绩及趋势</p><p class="placeholder-text">功能开发中…</p>`,
  homework: `<p class="detail-title">作业列表与提交状态</p><p class="placeholder-text">功能开发中…</p>`,
  exams: `<p class="detail-title">考试安排与考场信息</p><p class="placeholder-text">功能开发中…</p>`,
  mistakes: `<p class="detail-title">错题回顾与分类</p><p class="placeholder-text">功能开发中…</p>`,
  schedule: `<p class="detail-title">每周课表</p><p class="placeholder-text">功能开发中…</p>`,
}

function enterModule(tab: string) {
  if (isEntered.value) { switchTab(tab); return }
  // 激活主导航栏的模块模式（会触发 onModuleTabChange 回调设置内容）
  enterModuleMode(tab)
  isEntered.value = true
  // Pre-set hidden state for detail section animation
  gsap.set(".detail-section", { opacity: 0, y: 30 })
  const tl = gsap.timeline()
  tl.to("#unifiedGrid", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" })
  tl.to("#heroSection", { minHeight: 0, height: 0, padding: 0, overflow: "hidden", duration: 0.45, ease: "power3.inOut" }, "-=0.15")
  tl.call(() => { quoteVisible.value = true })
  tl.to(".detail-section", { y: 0, opacity: 1, duration: 0.4, ease: "power2.out" })
}

function goBack() {
  if (!isEntered.value) return
  const tl = gsap.timeline()
  tl.to(".detail-section", { opacity: 0, y: 20, duration: 0.25 })
  tl.call(() => {
    isEntered.value = false
    activeTab.value = ""
    quoteVisible.value = true
    nextTick(() => {
      gsap.fromTo("#heroSection",
        { minHeight: 0, height: 0, padding: 0, overflow: "hidden" },
        { minHeight: "calc(100vh - 56px)", height: "calc(100vh - 56px)", padding: "0 60px 20px", overflow: "visible", duration: 0.5, ease: "power3.out" }
      )
      gsap.fromTo("#unifiedGrid", { y: 0, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4 })
    })
  })
}

function toggleFlip() {
  if (!isEntered.value) isFlipped.value = !isFlipped.value
}

function switchTab(tab: string) {
  activeTab.value = tab
  gsap.to(".detail-content", {
    opacity: 0, y: 10, duration: 0.15,
    onComplete: () => {
      detailHTML.value = tabData[tab]
      nextTick(() => gsap.fromTo(".detail-content", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25 }))
    }
  })
}

onMounted(() => {
  pickRandom()
  gsap.from(".hero", { opacity: 0, y: 40, duration: 0.8, ease: "power3.out" })
  // 注册模块标签切换回调（由 Layout.vue 导航栏触发）
  registerModuleTabChange((tab: string) => {
    activeTab.value = tab
    detailHTML.value = tabData[tab]
    if (isEntered.value) {
      gsap.to(".detail-content", {
        opacity: 0, y: 10, duration: 0.15,
        onComplete: () => {
          nextTick(() => gsap.fromTo(".detail-content", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25 }))
        }
      })
    }
  })
  // 注册返回首页回调（由 Layout.vue 的 ← 首页按钮触发）
  registerBackToHome(() => { goBack() })
})
</script>

<template>
  <div class="learn-page">
    <div v-if="quoteVisible" id="heroSection" class="hero">
      <div id="unifiedGrid" class="unified-grid">
        <div class="quote-cell">
          <div :class="['flip-card', { flipped: isFlipped }]" id="flipCard">
            <div class="flip-front">
              <p class="quote-text" v-html="currentQuote.text"></p>
              <p class="quote-author">—— {{ currentQuote.author }}</p>
              <p class="flip-hint" @click.stop="toggleFlip">翻看介绍</p>
            </div>
            <div class="flip-back">
              <div class="author-avatar">{{ currentQuote.author[0] }}</div>
              <p class="author-name">{{ currentQuote.author }}</p>
              <p class="author-era">{{ currentQuote.era }}</p>
              <p class="author-desc">{{ currentQuote.desc }}</p>
              <p class="flip-hint" @click.stop="toggleFlip">翻回名言</p>
            </div>
          </div>
        </div>
        <div
          v-for="item in [
            { id: 'scores', label: '成绩' },
            { id: 'homework', label: '作业' },
            { id: 'exams', label: '考试' },
            { id: 'mistakes', label: '错题本' },
            { id: 'schedule', label: '课表' },
          ]"
          :key="item.id"
          class="module-cell"
          @click="enterModule(item.id)"
        >
          <span class="module-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <div v-show="isEntered" class="detail-section">
      <div class="detail-body">
        <Scores v-if="activeTab === 'scores'" activeTab="scores" />
        <div v-else class="detail-content" v-html="detailHTML"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Color overrides: warm palette + blue accents ── */
.learn-page {
  min-height: calc(100vh - 56px);
  --color-bg: #FFFFFF;
  --color-bg-card: #FFFFFF;
  --color-border: #E5E7EB;
}

/* ── Hero ── */
.hero {
  height: calc(100vh - 56px);
  display: flex; align-items: stretch; justify-content: center;
  padding: 0 60px 20px;
}

/* ── Grid: full width, no internal padding (hero handles spacing) ── */
.unified-grid {
  width: 100%;
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 1px; background: #000000;
  border: 1px solid #000000; overflow: hidden;
}

/* ── Quote cell ── */
.quote-cell {
  grid-column: 1 / -1;
  background: var(--color-bg-card);
  min-height: 320px; perspective: 1200px;
}
.flip-card {
  width: 100%; height: 100%; position: relative;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.flip-card.flipped { transform: rotateX(180deg); }
.flip-front, .flip-back {
  position: absolute; inset: 0;
  backface-visibility: hidden; -webkit-backface-visibility: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 40px;
}
.flip-front .quote-text {
  font-size: 32px; font-weight: 700; line-height: 1.6;
  color: var(--color-text); letter-spacing: 2px; margin-bottom: 12px; text-align: center;
  font-family: "Noto Serif SC", "Microsoft YaHei", serif;
}
.flip-front .quote-author {
  font-size: 14px; color: var(--color-text-light); letter-spacing: 4px;
}
.flip-front .flip-hint, .flip-back .flip-hint {
  position: absolute; bottom: 20px; font-size: 11px; color: var(--color-text-light);
  letter-spacing: 3px; cursor: pointer; animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 0.8; } }

.flip-back {
  background: var(--color-bg-card); transform: rotateX(180deg);
}
.flip-back .author-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; margin-bottom: 14px;
}
.flip-back .author-name { font-size: 20px; font-weight: 700; letter-spacing: 3px; margin-bottom: 6px; }
.flip-back .author-era { font-size: 12px; color: var(--color-text-light); letter-spacing: 2px; margin-bottom: 12px; }
.flip-back .author-desc { font-size: 13px; color: var(--color-text-secondary); text-align: center; line-height: 1.8; max-width: 480px; }

/* ── Module cells ── */
.module-cell {
  background: var(--color-bg-card); padding: 36px 12px;
  text-align: center; cursor: pointer; min-height: 90px;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.module-cell::before {
  content: ''; position: absolute; inset: 0;
  background: rgb(10, 11, 8); opacity: 0; transition: opacity 0.35s;
}
.module-cell:hover::before { opacity: 1; }
.module-cell:hover { color: #fff; }
.module-cell:hover .module-label { transform: translateY(-2px); letter-spacing: 4px; }
.module-label {
  font-size: 15px; font-weight: 700; letter-spacing: 3px;
  position: relative; z-index: 1; transition: all 0.35s;
}

/* ── Detail section (full width, aligned with hero) ── */
.detail-section {
  width: 100%; padding: 0 60px 80px;
}
.detail-body {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: 16px; padding: 32px; min-height: 360px;
}
.detail-title {
  font-size: 13px; color: var(--color-text-light); letter-spacing: 2px;
  margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f5f5f5;
}

/* ── Placeholder ── */
.placeholder-text {
  color: var(--color-text-light); font-size: 14px;
  letter-spacing: 1px; padding: 40px 0; text-align: center;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .module-cell { padding: 24px 8px; min-height: 70px; }
  .module-label { font-size: 13px; letter-spacing: 1px; }
  .flip-front .quote-text { font-size: 24px; }
  .quote-cell { min-height: 240px; }
}
</style>
