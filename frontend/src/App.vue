<template>
  <div class="garden-canvas">
    <svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="glow1" cx="15%" cy="20%" r="25%"><stop offset="0%" stop-color="#5a8f5c" stop-opacity="0.1"/><stop offset="100%" stop-color="#5a8f5c" stop-opacity="0"/></radialGradient>
        <radialGradient id="glow2" cx="85%" cy="75%" r="30%"><stop offset="0%" stop-color="#e8743f" stop-opacity="0.07"/><stop offset="100%" stop-color="#e8743f" stop-opacity="0"/></radialGradient>
      </defs>
      <rect fill="url(#glow1)" width="1440" height="900"/>
      <rect fill="url(#glow2)" width="1440" height="900"/>
    </svg>
  </div>

  <div class="leaf-float" style="top:18%;left:4%"><span style="width:20px;height:34px;animation-delay:0s"></span></div>
  <div class="leaf-float" style="top:35%;right:5%"><span style="width:16px;height:28px;animation-delay:5s"></span></div>
  <div class="leaf-float" style="top:60%;left:2%"><span style="width:18px;height:30px;animation-delay:10s"></span></div>

  <!-- First-time Guide Overlay -->
  <div class="guide-overlay" v-if="showGuide">
    <div class="guide-backdrop" @click="dismissGuide"></div>
    <div class="guide-dialog" :class="'step-' + guideStep">
      <button class="guide-close" @click="dismissGuide">&times;</button>
      <div class="guide-arrow" v-if="guideStep === 0">↓</div>
      <h3>{{ t.guideTitle }}</h3>
      <p>{{ guideSteps[guideStep] }}</p>
      <div class="guide-dots">
        <span v-for="i in guideSteps.length" :key="i" :class="{ active: i - 1 === guideStep }"></span>
      </div>
      <div class="guide-actions">
        <button class="guide-skip" @click="dismissGuide">{{ t.guideSkip }}</button>
        <button class="guide-next" @click="nextGuideStep">
          {{ guideStep < guideSteps.length - 1 ? t.guideNext : t.guideDone }}
        </button>
      </div>
    </div>
  </div>

  <div class="app-shell" :class="{ dark: darkMode }">
    <header class="hero">
      <div class="hero-inner">
        <div class="brand">
          <div class="brand-icon">
            <svg viewBox="0 0 100 100" width="38" height="38">
              <defs>
                <radialGradient id="lcGrad" cx="40%" cy="35%" r="55%">
                  <stop offset="0%" stop-color="#ff6b6b"/>
                  <stop offset="70%" stop-color="#c0392b"/>
                  <stop offset="100%" stop-color="#922b21"/>
                </radialGradient>
              </defs>
              <circle cx="50" cy="54" r="34" fill="url(#lcGrad)"/>
              <g fill="#922b21" opacity="0.4">
                <circle cx="34" cy="38" r="4"/><circle cx="52" cy="32" r="3.5"/>
                <circle cx="68" cy="42" r="4"/><circle cx="65" cy="62" r="3.5"/>
                <circle cx="38" cy="68" r="4"/><circle cx="28" cy="54" r="3.5"/>
                <circle cx="50" cy="46" r="3"/><circle cx="42" cy="56" r="3"/>
              </g>
              <ellipse cx="44" cy="18" rx="6" ry="10" fill="#27ae60" transform="rotate(-15,44,18)"/>
              <ellipse cx="56" cy="16" rx="5" ry="9" fill="#2ecc71" transform="rotate(10,56,16)"/>
              <path d="M50 20 Q50 10 50 5" stroke="#1e8449" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
          <div>
            <h1>{{ t.appName }}</h1>
            <p class="tagline">{{ t.tagline }}</p>
          </div>
        </div>
        <div class="hero-actions">
          <button class="icon-btn" @click="toggleDark" :title="t.darkMode">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path v-if="darkMode" d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/><circle v-else cx="12" cy="12" r="5"/><line v-if="!darkMode" x1="12" y1="1" x2="12" y2="3"/><line v-if="!darkMode" x1="12" y1="21" x2="12" y2="23"/><line v-if="!darkMode" x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line v-if="!darkMode" x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line v-if="!darkMode" x1="1" y1="12" x2="3" y2="12"/><line v-if="!darkMode" x1="21" y1="12" x2="23" y2="12"/><line v-if="!darkMode" x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line v-if="!darkMode" x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          </button>
          <button class="icon-btn lang-btn" @click="toggleLang" :title="t.switchLang">
            {{ lang === 'zh' ? 'EN' : '中' }}
          </button>
          <a class="icon-btn" href="https://github.com/porridgeowefish/lizhi" target="_blank" rel="noreferrer" title="GitHub">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          </a>
          <button class="sync-button" :disabled="syncing" @click="runSync">
            {{ syncing ? t.syncing : t.syncNow }}
          </button>
          <div class="job-chip" v-if="lastSyncJob">
            {{ t.discarded }} {{ lastSyncJob.posts_discarded }}
          </div>
        </div>
      </div>
    </header>

    <main class="page">
      <section class="toolbar card">
        <div class="toolbar-grid">
          <input v-model="draftSearch" @keyup.enter="applyFilters" :placeholder="t.searchPlaceholder" />
          <select v-model="filters.category" @change="applyFilters">
            <option value="">{{ t.allCategories }}</option>
            <option v-for="item in categoryOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
          <div class="sort-toggle">
            <button :class="{ active: filters.sort === 'deadline' }" @click="setSort('deadline')">{{ t.sortByDeadline }}</button>
            <button :class="{ active: filters.sort === 'published' }" @click="setSort('published')">{{ t.sortByPublished }}</button>
          </div>
          <div class="time-range-toggle">
            <button :class="{ active: filters.time_range === '' }" @click="setTimeRange('')">{{ t.allTime }}</button>
            <button :class="{ active: filters.time_range === 'this_week' }" @click="setTimeRange('this_week')">{{ t.thisWeek }}</button>
            <button :class="{ active: filters.time_range === 'this_weekend' }" @click="setTimeRange('this_weekend')">{{ t.thisWeekend }}</button>
            <button :class="{ active: filters.time_range === 'next_week' }" @click="setTimeRange('next_week')">{{ t.nextWeek }}</button>
          </div>
        </div>
      </section>

      <section class="content-grid">
        <div class="list-column">
          <div class="list-head">
            <h2>{{ t.opportunityList }} <small v-if="total">{{ total }} {{ t.items }}</small></h2>
            <button class="ghost" v-if="activeSearch" @click="clearSearch">{{ t.clearSearch }}</button>
          </div>

          <div v-if="errorMessage" class="card state error">{{ errorMessage }}</div>
          <div v-else-if="loading" class="card state loading-state">
            <div class="lychee-loader">
              <svg viewBox="0 0 60 60" width="48" height="48">
                <circle cx="30" cy="30" r="24" fill="#c0392b" class="lychee-body"/>
                <circle cx="30" cy="30" r="22" fill="#e74c3c"/>
                <g class="lychee-bumps">
                  <circle cx="20" cy="18" r="3" fill="#c0392b" opacity="0.5"/>
                  <circle cx="35" cy="15" r="2.5" fill="#c0392b" opacity="0.5"/>
                  <circle cx="42" cy="24" r="3" fill="#c0392b" opacity="0.5"/>
                  <circle cx="40" cy="38" r="2.5" fill="#c0392b" opacity="0.5"/>
                  <circle cx="25" cy="42" r="3" fill="#c0392b" opacity="0.5"/>
                  <circle cx="15" cy="32" r="2.5" fill="#c0392b" opacity="0.5"/>
                </g>
                <ellipse cx="30" cy="10" rx="4" ry="6" fill="#27ae60" class="lychee-leaf"/>
                <path d="M30 10 L30 4" stroke="#27ae60" stroke-width="1.5" stroke-linecap="round" class="lychee-stem"/>
              </svg>
              <span class="loading-text">{{ t.loading }}</span>
            </div>
          </div>
          <div v-else-if="posts.length === 0" class="card state">
            {{ t.noResults }}
          </div>

          <article
            v-for="post in posts"
            :key="post.id"
            class="card post-card"
            :class="{ selected: expandedId === post.id }"
            @click="toggleExpand(post)"
          >
            <div class="post-topline">
              <span class="pill tag-sm" :class="'tag-' + post.primary_category">{{ categoryLabel(post.primary_category) }}</span>
              <span class="post-date">{{ formatDate(post.published_at) }}</span>
            </div>
            <h3>{{ post.llm_title || post.title }}</h3>
            <p class="summary">{{ post.llm_summary || post.summary }}</p>
            <div class="post-bottom" v-if="post.deadline_at || post.source_name">
              <span class="deadline-tag" v-if="post.deadline_at">{{ t.deadline }} {{ formatDate(post.deadline_at) }}</span>
              <span class="source-tag">{{ post.source_name }}</span>
            </div>
            <div class="post-expand" v-if="expandedId === post.id">
              <dl class="expand-grid" v-if="hasAnyTime(post)">
                <div v-if="post.event_start_at"><dt>{{ t.startTime }}</dt><dd>{{ formatDate(post.event_start_at) }}</dd></div>
                <div v-if="post.event_end_at"><dt>{{ t.endTime }}</dt><dd>{{ formatDate(post.event_end_at) }}</dd></div>
                <div v-if="post.deadline_at"><dt>{{ t.deadlineTime }}</dt><dd>{{ formatDate(post.deadline_at) }}</dd></div>
              </dl>
              <a class="open-link" :href="post.original_url" target="_blank" rel="noreferrer">{{ t.viewOriginal }}</a>
            </div>
          </article>

          <div class="load-more-wrap" v-if="posts.length && posts.length < total">
            <button class="ghost" :disabled="loadingMore" @click="loadMore">
              {{ loadingMore ? t.loading : t.loadMore }}
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer class="app-footer">
      <div class="footer-brand">{{ t.appName }} · {{ t.tagline }}</div>
      <div class="footer-team">{{ t.devTeam }}</div>
    </footer>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { getPostCategories, getPosts, syncNow } from './api.js'

const I18N = {
  zh: {
    appName: '荔知', tagline: '荔园花园 · 深大信息聚合', syncNow: '立即同步', syncing: '同步中...',
    discarded: '丢弃', searchPlaceholder: '搜索讲座、活动、志愿...',
    allCategories: '全部', sortByDeadline: '按截止时间', sortByPublished: '按发布时间',
    allTime: '全部', thisWeek: '这周', thisWeekend: '这周末', nextWeek: '下周',
    opportunityList: '机会列表', clearSearch: '清除搜索',
    items: '条',
    loading: '正在加载...', noResults: '当前筛选条件下没有机会内容。你可以切换分类，或搜索更宽泛的关键词。',
    deadline: '截止', loadMore: '加载更多', startTime: '开始时间', endTime: '结束时间',
    deadlineTime: '截止时间', notRecognized: '未识别', viewOriginal: '查看原文',
    selectHint: '从左侧选择一条机会内容，这里会显示详情。',
    darkMode: '切换夜间模式', switchLang: 'Switch to English',
    devTeam: '哈基米南北绿豆',
    guideTitle: '使用指南', guideSkip: '跳过', guideNext: '下一步', guideDone: '开始使用',
    club_activity: '校园活动', lecture: '讲座论坛', volunteer: '志愿公益',
    competition: '竞赛征集', exam: '考试考核', recruitment: '招聘招募', notice: '通知公告', other: '其他',
  },
  en: {
    appName: 'Lizhi', tagline: 'SZU Campus Info Hub', syncNow: 'Sync Now', syncing: 'Syncing...',
    discarded: 'Discarded', searchPlaceholder: 'Search lectures, events...',
    allCategories: 'All', sortByDeadline: 'By Deadline', sortByPublished: 'By Published',
    allTime: 'All', thisWeek: 'This Week', thisWeekend: 'This Weekend', nextWeek: 'Next Week',
    opportunityList: 'Opportunities', clearSearch: 'Clear',
    items: 'items',
    loading: 'Loading...', noResults: 'No results found. Try different filters or keywords.',
    deadline: 'Due', loadMore: 'Load More', startTime: 'Start', endTime: 'End',
    deadlineTime: 'Deadline', notRecognized: 'N/A', viewOriginal: 'View Original',
    selectHint: 'Select an item from the list to view details.',
    darkMode: 'Toggle Dark Mode', switchLang: '切换中文',
    devTeam: 'Hajimi Nanbei Lvdou',
    guideTitle: 'Quick Guide', guideSkip: 'Skip', guideNext: 'Next', guideDone: 'Get Started',
    club_activity: 'Activity', lecture: 'Lecture', volunteer: 'Volunteer',
    competition: 'Competition', exam: 'Exam', recruitment: 'Recruitment', notice: 'Notice', other: 'Other',
  },
}

const CATEGORY_KEYS = ['club_activity', 'lecture', 'volunteer', 'competition', 'exam', 'recruitment', 'notice', 'other']

export default {
  name: 'App',
  setup() {
    const posts = ref([])
    const total = ref(0)
    const stats = ref({ categories: [], content_type_stats: {}, participation_stats: {}, time_status_stats: {} })
    const expandedId = ref(null)
    const loading = ref(false)
    const loadingMore = ref(false)
    const syncing = ref(false)
    const errorMessage = ref('')
    const draftSearch = ref('')
    const activeSearch = ref('')
    const offset = ref(0)
    const lastSyncJob = ref(null)
    const filters = ref({ category: '', time_range: '', sort: 'deadline' })

    const lang = ref(localStorage.getItem('lizhi-lang') || 'zh')
    const darkMode = ref(localStorage.getItem('lizhi-dark') === 'true')

    const showGuide = ref(false)
    const guideStep = ref(0)

    const t = computed(() => I18N[lang.value])

    const guideStepsZh = [
      '在搜索框输入关键词，快速查找讲座、活动、竞赛等信息。',
      '使用分类筛选和「这周/这周末/下周」按钮，快速定位感兴趣的时间段。',
      '点击「按截止时间」查看最紧急的机会，或「按发布时间」看最新内容。',
      '点击任意一条机会，右侧会显示详情、时间信息和原文链接。',
    ]
    const guideStepsEn = [
      'Type keywords in the search box to find lectures, events, and more.',
      'Use category filter and time range buttons to narrow results.',
      'Sort by deadline for urgency, or by published date for recency.',
      'Click any item to view full details, time info, and source link.',
    ]
    const guideSteps = computed(() => lang.value === 'zh' ? guideStepsZh : guideStepsEn)

    const categoryOptions = computed(() =>
      CATEGORY_KEYS.map(key => ({ value: key, label: t.value[key] || key })),
    )

    function categoryLabel(key) { return t.value[key] || key || '' }

    function setTimeRange(range) {
      filters.value.time_range = range
      selectedPost.value = null
      loadPosts()
    }

    function toggleLang() {
      lang.value = lang.value === 'zh' ? 'en' : 'zh'
      localStorage.setItem('lizhi-lang', lang.value)
    }
    function toggleDark() {
      darkMode.value = !darkMode.value
      localStorage.setItem('lizhi-dark', String(darkMode.value))
    }
    function dismissGuide() {
      showGuide.value = false
      localStorage.setItem('lizhi-guide-done', '1')
    }
    function nextGuideStep() {
      if (guideStep.value < guideSteps.value.length - 1) { guideStep.value++ }
      else { dismissGuide() }
    }

    function buildParams(nextOffset = 0) {
      const params = { offset: nextOffset, limit: 20 }
      if (filters.value.category) params.category = filters.value.category
      if (filters.value.time_range) params.time_range = filters.value.time_range
      if (filters.value.sort) params.sort = filters.value.sort
      if (activeSearch.value) params.search = activeSearch.value
      return params
    }

    async function loadPosts({ append = false } = {}) {
      if (!append) { loading.value = true; errorMessage.value = '' }
      try {
        const payload = await getPosts(buildParams(append ? offset.value : 0))
        posts.value = append ? [...posts.value, ...payload.items] : payload.items
        total.value = payload.total
        offset.value = posts.value.length
      } catch (error) {
        errorMessage.value = error?.response?.data?.detail || 'Failed to load data.'
      } finally { loading.value = false; loadingMore.value = false }
    }

    async function loadStats() { stats.value = await getPostCategories() }
    function toggleExpand(post) { expandedId.value = expandedId.value === post.id ? null : post.id }
    function applyFilters() { activeSearch.value = draftSearch.value.trim(); expandedId.value = null; loadPosts() }
    function clearSearch() { draftSearch.value = ''; activeSearch.value = ''; loadPosts() }
    function setSort(mode) { filters.value.sort = mode; expandedId.value = null; loadPosts() }
    function loadMore() { loadingMore.value = true; loadPosts({ append: true }) }
    function hasAnyTime(post) { return post.event_start_at || post.event_end_at || post.deadline_at }
    async function runSync() {
      syncing.value = true
      try { lastSyncJob.value = await syncNow(); await Promise.all([loadPosts(), loadStats()]) }
      finally { syncing.value = false }
    }
    function formatDate(value) {
      if (!value) return ''
      const d = new Date(value)
      return Number.isNaN(d.getTime()) ? '' : `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    }

    onMounted(async () => {
      await Promise.all([loadPosts(), loadStats()])
      if (!localStorage.getItem('lizhi-guide-done')) { showGuide.value = true }
    })

    return {
      posts, total, stats, expandedId, loading, loadingMore, syncing, errorMessage,
      draftSearch, activeSearch, filters, lastSyncJob,
      lang, darkMode, t, showGuide, guideStep, guideSteps,
      categoryOptions, categoryLabel,
      toggleLang, toggleDark, dismissGuide, nextGuideStep,
      applyFilters, clearSearch, setSort, setTimeRange, toggleExpand, loadMore, runSync, formatDate, hasAnyTime,
    }
  },
}
</script>

<style>
/* === Garden Design System === */
:root {
  --bg: #f0f7ed;
  --card: #ffffff;
  --line: #c8dcc3;
  --text: #2d3a29;
  --muted: #6b7a66;
  --primary: #5a8f5c;
  --accent: #e8743f;
  --soft: #e8f5e9;
  --title-font: 'ZCOOL XiaoWei', serif;
  --body-font: 'LXGW WenKai TC', -apple-system, 'PingFang SC', sans-serif;
  --tag-font: 'Nunito', sans-serif;
  --tag-club_activity: #d4edda; --tag-club_activity-fg: #2d6a3e;
  --tag-lecture: #d6eaf8; --tag-lecture-fg: #1a5276;
  --tag-volunteer: #fdebd0; --tag-volunteer-fg: #b9770e;
  --tag-exam: #fadbd8; --tag-exam-fg: #922b21;
  --tag-recruitment: #d1f2eb; --tag-recruitment-fg: #0e6655;
  --tag-competition: #e8daef; --tag-competition-fg: #6c3483;
  --tag-notice: #d5f5e3; --tag-notice-fg: #1e8449;
  --tag-other: #eaecee; --tag-other-fg: #5d6d7e;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: var(--body-font);
  background:
    radial-gradient(ellipse at 15% 20%, rgba(90,143,92,0.12) 0%, transparent 70%),
    radial-gradient(ellipse at 85% 75%, rgba(232,116,63,0.08) 0%, transparent 70%),
    radial-gradient(ellipse at 50% 10%, rgba(139,195,74,0.06) 0%, transparent 70%),
    var(--bg);
  color: var(--text);
  line-height: 1.6;
}

button, input, select { font: inherit; }

/* === Organic Background Canvas === */
.garden-canvas {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
}
.garden-canvas svg { width: 100%; height: 100%; }

/* === Floating Leaf Particles === */
.leaf-float {
  position: fixed; pointer-events: none; z-index: 0; opacity: 0.18;
}
.leaf-float span {
  display: block; border-radius: 50% 0 50% 50%;
  background: linear-gradient(135deg, var(--primary), #8bc34a);
  animation: leafDrift 20s ease-in-out infinite;
}
@keyframes leafDrift {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-18px) rotate(8deg); }
  50% { transform: translateY(6px) rotate(-5deg); }
  75% { transform: translateY(-10px) rotate(3deg); }
}

/* === Layout Shell === */
.app-shell {
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* === Hero Header with Green Gradient === */
.hero {
  background: linear-gradient(160deg, #3d7a3f 0%, #5a8f5c 35%, #72a874 65%, #8bb890 100%);
  color: #fff;
  position: relative;
  z-index: 100;
  padding-bottom: 32px;
  box-shadow: 0 6px 30px rgba(45,58,41,0.18);
}
.hero::after {
  content: '';
  position: absolute; bottom: -2px; left: 0; right: 0;
  height: 40px;
  background: var(--bg);
  border-radius: 50% 50% 0 0 / 100% 100% 0 0;
}

.hero-inner, .page {
  max-width: 1280px;
  margin: 0 auto;
}

.hero-inner {
  padding: 22px 24px 0;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

/* === Brand Icon === */
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}
.brand-icon {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #c0392b, #e74c3c);
  display: flex; align-items: center; justify-content: center;
  border-radius: 18px;
  box-shadow: 0 4px 16px rgba(192,57,43,0.35);
  position: relative;
  overflow: hidden;
}
.brand h1 {
  font-family: var(--title-font);
  font-size: 26px;
  letter-spacing: 4px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
  margin: 0;
}
.brand .tagline {
  font-size: 12px;
  opacity: 0.8;
  letter-spacing: 1.5px;
  margin-top: 2px;
}

.hero-copy {
  display: none;
}

.hero-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* === Toolbar / Category Nav === */
.toolbar {
  background: var(--card);
  border: none;
  border-bottom: 1px solid var(--line);
  border-radius: 0;
  box-shadow: 0 2px 12px rgba(45,58,41,0.06);
  position: sticky;
  top: 0;
  z-index: 90;
  padding: 12px 0;
}

.toolbar-grid {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.toolbar-grid::-webkit-scrollbar { display: none; }

.toolbar-grid label {
  display: contents;
}
.toolbar-grid label span {
  display: none;
}
.toolbar-grid input,
.toolbar-grid select {
  display: inline-flex;
  align-items: center;
  padding: 7px 20px;
  border: 1.5px solid var(--line);
  border-radius: 100px;
  background: transparent;
  color: var(--muted);
  font-family: var(--tag-font);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
  min-width: auto;
  width: auto;
  flex-shrink: 0;
}
.toolbar-grid input {
  min-width: 180px;
  padding-left: 36px;
  background: rgba(90,143,92,0.04) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7a66' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") 14px center no-repeat;
}
.toolbar-grid input::placeholder {
  color: var(--muted);
  font-weight: 400;
}
.toolbar-grid input:focus,
.toolbar-grid select:focus {
  border-color: var(--primary);
  color: var(--primary);
  background-color: rgba(90,143,92,0.06);
  outline: none;
}
.toolbar-grid select:focus {
  background: rgba(90,143,92,0.06);
}
.sort-toggle {
  display: flex;
  gap: 0;
  border: 1.5px solid var(--line);
  border-radius: 100px;
  overflow: hidden;
}
.sort-toggle button {
  padding: 7px 14px;
  font-size: 0.82rem;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.sort-toggle button.active {
  background: var(--primary);
  color: #fff;
}
.sort-toggle button:not(.active):hover {
  background: rgba(90,143,92,0.08);
}
.time-range-toggle {
  display: flex;
  gap: 0;
  border: 1.5px solid var(--line);
  border-radius: 100px;
  overflow: hidden;
}
.time-range-toggle button {
  padding: 7px 12px;
  font-size: 0.82rem;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  white-space: nowrap;
}
.time-range-toggle button.active {
  background: var(--primary);
  color: #fff;
}
.time-range-toggle button:not(.active):hover {
  background: rgba(90,143,92,0.08);
}

/* === Page & Content Grid === */
.page {
  padding: 28px 24px 40px;
}

/* === Content Grid === */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.list-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.list-head h2 {
  margin: 0;
  font-family: var(--title-font);
  color: var(--primary);
  position: relative;
}
.list-head h2::after {
  content: '';
  display: block;
  width: 40px; height: 3px;
  background: linear-gradient(90deg, var(--accent), transparent);
  border-radius: 2px;
  margin-top: 6px;
}

.list-column { min-width: 0; }

/* === Post Cards with Leaf Decorations === */
.card {
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 20px;
  box-shadow: 0 2px 14px rgba(45,58,41,0.06);
}

.post-card {
  padding: 22px 22px 18px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.35s ease, box-shadow 0.35s ease;
  position: relative;
  overflow: visible;
  animation: growIn 0.5s ease both;
}
.post-card::before {
  content: '';
  position: absolute; top: -6px; right: -4px;
  width: 36px; height: 20px;
  background: linear-gradient(135deg, rgba(90,143,92,0.3), rgba(139,195,74,0.1));
  border-radius: 0 50% 0 50%;
  transform: rotate(30deg);
  z-index: 2;
  transition: transform 0.3s, opacity 0.3s;
}
.post-card:hover {
  transform: scale(1.02) translateY(-4px);
  box-shadow: 0 12px 36px rgba(45,58,41,0.13), 0 4px 12px rgba(90,143,92,0.08);
  border-color: var(--primary);
}
.post-card:hover::before {
  transform: rotate(40deg) scale(1.15);
  opacity: 0.9;
}
.post-card.selected {
  transform: scale(1.02) translateY(-4px);
  box-shadow: 0 12px 36px rgba(45,58,41,0.13), 0 4px 12px rgba(90,143,92,0.08);
  border-color: var(--primary);
}
@keyframes growIn {
  from { opacity: 0; transform: scale(0.94) translateY(16px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.post-topline,
.score-row,
.detail-topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
  font-family: var(--tag-font);
}

.post-card h3,
.detail-card h2 {
  margin: 12px 0 10px;
  line-height: 1.35;
  font-family: var(--title-font);
  transition: color 0.2s;
}
.post-card:hover h3 {
  color: var(--primary);
}

.summary, .detail-summary {
  color: var(--muted);
  line-height: 1.7;
}

.meta-row, .detail-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0;
}

/* === Category-Specific Pill Colors === */
.pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  border-radius: 100px;
  font-family: var(--tag-font);
  font-size: 11px;
  font-weight: 700;
  background: var(--soft);
  color: var(--text);
  transition: transform 0.2s;
}
.pill:hover { transform: scale(1.06); }

.pill.tag-club_activity { background: var(--tag-club_activity); color: var(--tag-club_activity-fg); }
.pill.tag-lecture { background: var(--tag-lecture); color: var(--tag-lecture-fg); }
.pill.tag-volunteer { background: var(--tag-volunteer); color: var(--tag-volunteer-fg); }
.pill.tag-exam { background: var(--tag-exam); color: var(--tag-exam-fg); }
.pill.tag-recruitment { background: var(--tag-recruitment); color: var(--tag-recruitment-fg); }
.pill.tag-competition { background: var(--tag-competition); color: var(--tag-competition-fg); }
.pill.tag-notice { background: var(--tag-notice); color: var(--tag-notice-fg); }
.pill.tag-other { background: var(--tag-other); color: var(--tag-other-fg); }

.pill.success { background: rgba(90,143,92,0.12); color: var(--primary); }
.pill.warning { background: rgba(232,116,63,0.12); color: var(--accent); }
.pill.muted { background: rgba(107,122,102,0.12); color: var(--muted); }

.score-row { margin-top: 10px; }
.pill.tag-sm {
  padding: 2px 8px;
  font-size: 10px;
}
.post-date {
  font-size: 12px;
  font-family: var(--tag-font);
  color: var(--muted);
}
.post-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  gap: 8px;
}
.deadline-tag {
  font-size: 12px;
  font-family: var(--tag-font);
  color: var(--accent);
  font-weight: 700;
}
.source-tag {
  font-size: 11px;
  font-family: var(--tag-font);
  color: var(--muted);
  opacity: 0.7;
}
.list-head small {
  font-size: 13px;
  font-weight: 400;
  color: var(--muted);
  margin-left: 8px;
}

/* === Inline Expand === */
.post-expand {
  border-top: 1px solid var(--line);
  margin-top: 12px;
  padding-top: 12px;
  animation: expandIn 0.25s ease;
}
@keyframes expandIn {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 200px; }
}
.expand-grid {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.expand-grid div {
  display: flex;
  gap: 6px;
  font-size: 12px;
}
.expand-grid dt {
  color: var(--muted);
  font-family: var(--tag-font);
}
.expand-grid dd {
  margin: 0;
}

.state {
  padding: 24px;
  color: var(--muted);
}
.state.error {
  color: #a13333;
  border-color: rgba(161,51,51,0.35);
}

/* === Lychee Loading Animation === */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 48px 24px !important;
}
.lychee-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.lychee-loader svg {
  animation: lycheeBounce 1.2s ease-in-out infinite;
}
.lychee-body {
  animation: lycheePeel 1.2s ease-in-out infinite;
}
.lychee-leaf {
  animation: lycheeSway 1.2s ease-in-out infinite;
  transform-origin: center bottom;
}
.loading-text {
  font-size: 0.85rem;
  color: var(--muted);
  animation: fadeInOut 1.2s ease-in-out infinite;
}
@keyframes lycheeBounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-6px) scale(1.05); }
}
@keyframes lycheePeel {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.92); }
}
@keyframes lycheeSway {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-8deg); }
  75% { transform: rotate(8deg); }
}
@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* === Buttons === */
.sync-button, .ghost, .open-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 100px;
  border: 1.5px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.15);
  color: #fff;
  text-decoration: none;
  cursor: pointer;
  font-family: var(--tag-font);
  font-size: 13px;
  font-weight: 700;
  transition: all 0.3s;
  backdrop-filter: blur(4px);
}
.sync-button:hover {
  background: rgba(255,255,255,0.28);
  transform: translateY(-1px);
}
.sync-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ghost {
  background: transparent;
  border-color: var(--primary);
  color: var(--primary);
}
.ghost:hover {
  background: var(--primary);
  color: #fff;
}

.job-chip {
  padding: 8px 12px;
  border-radius: 100px;
  background: rgba(255,255,255,0.15);
  color: #fff;
  font-size: 13px;
  font-family: var(--tag-font);
  backdrop-filter: blur(4px);
}

.load-more-wrap {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.open-link {
  background: transparent;
  border: none;
  color: var(--primary);
  padding: 0;
  font-size: 13px;
  position: relative;
  padding-bottom: 1px;
}
.open-link::after {
  content: '';
  position: absolute; bottom: 0; left: 0;
  width: 0; height: 1.5px;
  background: var(--accent);
  transition: width 0.3s;
  border-radius: 1px;
}
.open-link:hover {
  color: var(--accent);
}
.open-link:hover::after {
  width: 100%;
}

/* === Footer === */
.app-footer {
  text-align: center;
  padding: 32px 24px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--line);
  margin-top: 48px;
}
.app-footer::before {
  content: '';
  display: block;
  width: 60px; height: 3px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  border-radius: 2px;
  margin: 0 auto 16px;
}

/* === Dark Mode === */
.app-shell.dark {
  --bg: #1a1f1a;
  --card: #242a24;
  --line: #3a4a3a;
  --text: #d4e0d4;
  --muted: #8a9a8a;
  --primary: #7ab87c;
  --accent: #f09060;
  --soft: #2a3a2a;
}
.app-shell.dark body,
.app-shell.dark {
  background: #1a1f1a;
  color: #d4e0d4;
}
.app-shell.dark .hero {
  background: linear-gradient(160deg, #2a4a2c 0%, #3a6a3c 35%, #4a7a4c 65%, #5a8a5c 100%);
}
.app-shell.dark .toolbar {
  background: #242a24;
  border-bottom-color: #3a4a3a;
}
.app-shell.dark .toolbar-grid input {
  background: rgba(122,184,124,0.06) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238a9a8a' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") 14px center no-repeat;
}

/* === Icon Buttons (Lang / Dark / GitHub) === */
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.1);
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--tag-font);
  backdrop-filter: blur(4px);
}
.icon-btn:hover {
  background: rgba(255,255,255,0.25);
  transform: translateY(-1px);
}
.lang-btn {
  font-size: 11px;
  letter-spacing: 0.5px;
}

/* === Footer Team Credit === */
.footer-team {
  font-size: 11px;
  opacity: 0.4;
  margin-top: 6px;
  letter-spacing: 1px;
}

/* === Guide Overlay === */
.guide-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.guide-backdrop {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(3px);
}
.guide-dialog {
  position: relative;
  background: var(--card);
  color: var(--text);
  border-radius: 20px;
  padding: 32px 36px 24px;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  text-align: center;
  animation: guideIn 0.4s ease;
}
@keyframes guideIn {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.guide-close {
  position: absolute;
  top: 12px; right: 16px;
  background: none; border: none;
  font-size: 22px; color: var(--muted);
  cursor: pointer;
}
.guide-arrow {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 28px;
  color: var(--primary);
  animation: guideBounce 1.5s ease infinite;
}
@keyframes guideBounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-8px); }
}
.guide-dialog h3 {
  margin: 0 0 12px;
  font-family: var(--title-font);
  font-size: 22px;
  color: var(--primary);
}
.guide-dialog p {
  color: var(--muted);
  line-height: 1.7;
  margin: 0 0 16px;
}
.guide-dots {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-bottom: 18px;
}
.guide-dots span {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--line);
  transition: all 0.3s;
}
.guide-dots span.active {
  background: var(--primary);
  transform: scale(1.3);
}
.guide-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
.guide-skip, .guide-next {
  padding: 8px 20px;
  border-radius: 100px;
  font-family: var(--tag-font);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.guide-skip {
  background: transparent;
  border: 1.5px solid var(--line);
  color: var(--muted);
}
.guide-skip:hover {
  border-color: var(--muted);
  color: var(--text);
}
.guide-next {
  background: var(--primary);
  border: none;
  color: #fff;
}
.guide-next:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* === Responsive === */
@media (max-width: 980px) {
  .toolbar-grid,
  .stats-grid,
  .content-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .hero-inner {
    flex-direction: column;
    gap: 14px;
    text-align: center;
  }
  .brand { justify-content: center; }
  .hero-actions {
    margin-left: 0;
    justify-content: center;
  }
  .detail-card { position: static; }
  .toolbar-grid {
    display: flex;
    flex-wrap: nowrap;
    padding: 0 12px;
  }
  .post-card::before { display: none; }
}
</style>
