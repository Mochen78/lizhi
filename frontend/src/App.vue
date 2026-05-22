<template>
  <div class="app-shell">
    <header class="hero">
      <div class="hero-inner">
        <div>
          <p class="eyebrow">Iter-1 Opportunity Engine</p>
          <h1>校园机会雷达</h1>
          <p class="hero-copy">
            默认只显示仍值得参与的内容。回顾、教程、乱码源和无关记录型文章会在同步阶段被规则预筛剔除。
          </p>
        </div>
        <div class="hero-actions">
          <button class="sync-button" :disabled="syncing" @click="runSync">
            {{ syncing ? '同步中...' : '立即同步' }}
          </button>
          <div class="job-chip" v-if="lastSyncJob">
            丢弃 {{ lastSyncJob.posts_discarded }} 条
          </div>
        </div>
      </div>
    </header>

    <main class="page">
      <section class="toolbar card">
        <div class="toolbar-grid">
          <label>
            <span>搜索</span>
            <input v-model="draftSearch" @keyup.enter="applyFilters" placeholder="搜索讲座、竞赛、招聘..." />
          </label>
          <label>
            <span>分类</span>
            <select v-model="filters.category" @change="applyFilters">
              <option value="">全部分类</option>
              <option v-for="item in categoryOptions" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </label>
          <label>
            <span>参与状态</span>
            <select v-model="filters.participation_status" @change="applyFilters">
              <option value="">全部</option>
              <option value="participable">可参与</option>
              <option value="uncertain">待判断</option>
              <option value="non_participable">不可参与</option>
            </select>
          </label>
          <label>
            <span>时间状态</span>
            <select v-model="filters.time_status" @change="applyFilters">
              <option value="">全部</option>
              <option value="upcoming">即将开始</option>
              <option value="ongoing">进行中</option>
              <option value="undated">未明确时间</option>
              <option value="expired">已过期</option>
            </select>
          </label>
        </div>
      </section>

      <section class="stats-grid">
        <article class="card stat">
          <span>当前结果</span>
          <strong>{{ total }}</strong>
        </article>
        <article class="card stat">
          <span>可参与</span>
          <strong>{{ stats.participation_stats.participable || 0 }}</strong>
        </article>
        <article class="card stat">
          <span>待判断</span>
          <strong>{{ stats.participation_stats.uncertain || 0 }}</strong>
        </article>
        <article class="card stat">
          <span>即将开始</span>
          <strong>{{ stats.time_status_stats.upcoming || 0 }}</strong>
        </article>
      </section>

      <section class="content-grid">
        <div class="list-column">
          <div class="list-head">
            <h2>机会列表</h2>
            <button class="ghost" v-if="activeSearch" @click="clearSearch">清除搜索</button>
          </div>

          <div v-if="errorMessage" class="card state error">{{ errorMessage }}</div>
          <div v-else-if="loading" class="card state">正在加载机会数据...</div>
          <div v-else-if="posts.length === 0" class="card state">
            当前筛选条件下没有机会内容。你可以切换分类，或搜索更宽泛的关键词。
          </div>

          <article
            v-for="post in posts"
            :key="post.id"
            class="card post-card"
            :class="{ selected: selectedPost && selectedPost.id === post.id }"
            @click="openPost(post)"
          >
            <div class="post-topline">
              <span>{{ post.source_name }}</span>
              <span>{{ formatDate(post.published_at) }}</span>
            </div>
            <h3>{{ post.title }}</h3>
            <p class="summary">{{ post.summary }}</p>
            <div class="meta-row">
              <span class="pill primary">{{ categoryLabel(post.primary_category) }}</span>
              <span class="pill success" v-if="post.participation_status === 'participable'">可参与</span>
              <span class="pill warning" v-else-if="post.participation_status === 'uncertain'">待判断</span>
              <span class="pill muted" v-else>不可参与</span>
              <span class="pill">{{ timeLabel(post.time_status) }}</span>
            </div>
            <div class="score-row">
              <span>排序分 {{ post.ranking_score.toFixed(0) }}</span>
              <span v-if="post.deadline_at">截止 {{ formatDate(post.deadline_at) }}</span>
            </div>
          </article>

          <div class="load-more-wrap" v-if="posts.length && posts.length < total">
            <button class="ghost" :disabled="loadingMore" @click="loadMore">
              {{ loadingMore ? '加载中...' : '加载更多' }}
            </button>
          </div>
        </div>

        <aside class="detail-column">
          <div v-if="selectedPost" class="card detail-card">
            <div class="detail-topline">
              <span>{{ selectedPost.source_name }}</span>
              <span>{{ formatDate(selectedPost.published_at) }}</span>
            </div>
            <h2>{{ selectedPost.title }}</h2>
            <p class="detail-summary">{{ selectedPost.summary }}</p>

            <div class="detail-pills">
              <span class="pill primary">{{ categoryLabel(selectedPost.primary_category) }}</span>
              <span class="pill">{{ participationLabel(selectedPost.participation_status) }}</span>
              <span class="pill">{{ timeLabel(selectedPost.time_status) }}</span>
            </div>

            <dl class="detail-grid">
              <div>
                <dt>开始时间</dt>
                <dd>{{ formatDate(selectedPost.event_start_at) || '未识别' }}</dd>
              </div>
              <div>
                <dt>结束时间</dt>
                <dd>{{ formatDate(selectedPost.event_end_at) || '未识别' }}</dd>
              </div>
              <div>
                <dt>截止时间</dt>
                <dd>{{ formatDate(selectedPost.deadline_at) || '未识别' }}</dd>
              </div>
              <div>
                <dt>排序分</dt>
                <dd>{{ selectedPost.ranking_score.toFixed(0) }}</dd>
              </div>
            </dl>

            <div class="detail-html" v-if="selectedPost.content_html" v-html="selectedPost.content_html"></div>

            <a class="open-link" :href="selectedPost.original_url" target="_blank" rel="noreferrer">
              查看原文
            </a>
          </div>
          <div v-else class="card state">
            从左侧选择一条机会内容，这里会显示摘要、时间字段和清洗后的正文。
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { getPost, getPostCategories, getPosts, syncNow } from './api.js'

const CATEGORY_LABELS = {
  club_activity: '校园活动',
  lecture: '讲座论坛',
  volunteer: '志愿公益',
  competition: '竞赛征集',
  exam: '考试考核',
  recruitment: '招聘招募',
  notice: '通知公告',
  other: '其他',
}

export default {
  name: 'App',
  setup() {
    const posts = ref([])
    const total = ref(0)
    const stats = ref({
      categories: [],
      content_type_stats: {},
      participation_stats: {},
      time_status_stats: {},
    })
    const selectedPost = ref(null)
    const loading = ref(false)
    const loadingMore = ref(false)
    const syncing = ref(false)
    const errorMessage = ref('')
    const draftSearch = ref('')
    const activeSearch = ref('')
    const offset = ref(0)
    const lastSyncJob = ref(null)
    const filters = ref({
      category: '',
      participation_status: '',
      time_status: '',
    })

    const categoryOptions = computed(() =>
      Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label })),
    )

    function categoryLabel(key) {
      return CATEGORY_LABELS[key] || key || '未分类'
    }

    function participationLabel(key) {
      return {
        participable: '可参与',
        uncertain: '待判断',
        non_participable: '不可参与',
      }[key] || key
    }

    function timeLabel(key) {
      return {
        upcoming: '即将开始',
        ongoing: '进行中',
        expired: '已过期',
        undated: '未明确时间',
      }[key] || key
    }

    function buildParams(nextOffset = 0) {
      const params = {
        offset: nextOffset,
        limit: 20,
      }
      if (filters.value.category) params.category = filters.value.category
      if (filters.value.participation_status) params.participation_status = filters.value.participation_status
      if (filters.value.time_status) params.time_status = filters.value.time_status
      if (activeSearch.value) params.search = activeSearch.value
      return params
    }

    async function loadPosts({ append = false } = {}) {
      if (!append) {
        loading.value = true
        errorMessage.value = ''
      }
      try {
        const nextOffset = append ? offset.value : 0
        const payload = await getPosts(buildParams(nextOffset))
        posts.value = append ? [...posts.value, ...payload.items] : payload.items
        total.value = payload.total
        offset.value = posts.value.length
      } catch (error) {
        errorMessage.value = error?.response?.data?.detail || '加载数据失败，请稍后重试。'
      } finally {
        loading.value = false
        loadingMore.value = false
      }
    }

    async function loadStats() {
      stats.value = await getPostCategories()
    }

    async function openPost(post) {
      const full = await getPost(post.id)
      selectedPost.value = full
    }

    function applyFilters() {
      activeSearch.value = draftSearch.value.trim()
      selectedPost.value = null
      loadPosts()
    }

    function clearSearch() {
      draftSearch.value = ''
      activeSearch.value = ''
      loadPosts()
    }

    function loadMore() {
      loadingMore.value = true
      loadPosts({ append: true })
    }

    async function runSync() {
      syncing.value = true
      try {
        lastSyncJob.value = await syncNow()
        await Promise.all([loadPosts(), loadStats()])
      } finally {
        syncing.value = false
      }
    }

    function formatDate(value) {
      if (!value) return ''
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return ''
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    onMounted(async () => {
      await Promise.all([loadPosts(), loadStats()])
    })

    return {
      posts,
      total,
      stats,
      selectedPost,
      loading,
      loadingMore,
      syncing,
      errorMessage,
      draftSearch,
      activeSearch,
      filters,
      lastSyncJob,
      categoryOptions,
      categoryLabel,
      participationLabel,
      timeLabel,
      applyFilters,
      clearSearch,
      loadMore,
      openPost,
      runSync,
      formatDate,
    }
  },
}
</script>

<style>
:root {
  color-scheme: light;
  --bg: #f6f2e8;
  --card: rgba(255, 255, 255, 0.92);
  --line: #dbcdb4;
  --text: #2f2416;
  --muted: #6c5a42;
  --accent: #b95c2e;
  --accent-2: #2e6a57;
  --soft: #efe5d1;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, serif;
  background:
    radial-gradient(circle at top left, rgba(185, 92, 46, 0.12), transparent 30%),
    radial-gradient(circle at top right, rgba(46, 106, 87, 0.12), transparent 25%),
    var(--bg);
  color: var(--text);
}

button,
input,
select {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
}

.hero {
  padding: 48px 24px 28px;
}

.hero-inner,
.page {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-inner {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--accent);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

h1 {
  margin: 0;
  font-size: clamp(32px, 5vw, 56px);
  line-height: 1.05;
}

.hero-copy {
  max-width: 720px;
  margin: 16px 0 0;
  color: var(--muted);
  line-height: 1.75;
}

.hero-actions {
  display: grid;
  gap: 12px;
  justify-items: end;
}

.page {
  padding: 0 24px 40px;
}

.card {
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 22px;
  box-shadow: 0 16px 40px rgba(47, 36, 22, 0.06);
}

.toolbar {
  padding: 20px;
}

.toolbar-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
}

label span {
  font-size: 13px;
  color: var(--muted);
}

input,
select {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--text);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.stat {
  padding: 18px 20px;
}

.stat span {
  display: block;
  color: var(--muted);
  font-size: 13px;
}

.stat strong {
  display: block;
  margin-top: 6px;
  font-size: 32px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 20px;
}

.list-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-head h2 {
  margin: 0;
}

.list-column {
  min-width: 0;
}

.post-card {
  padding: 20px;
  margin-bottom: 14px;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.post-card:hover,
.post-card.selected {
  transform: translateY(-2px);
  border-color: var(--accent);
}

.post-topline,
.score-row,
.detail-topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}

.post-card h3,
.detail-card h2 {
  margin: 12px 0 10px;
  line-height: 1.35;
}

.summary,
.detail-summary {
  color: var(--muted);
  line-height: 1.7;
}

.meta-row,
.detail-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--soft);
  color: var(--text);
  font-size: 12px;
}

.pill.primary {
  background: rgba(185, 92, 46, 0.12);
  color: var(--accent);
}

.pill.success {
  background: rgba(46, 106, 87, 0.12);
  color: var(--accent-2);
}

.pill.warning {
  background: rgba(185, 92, 46, 0.14);
  color: var(--accent);
}

.pill.muted {
  background: rgba(108, 90, 66, 0.12);
  color: var(--muted);
}

.score-row {
  margin-top: 10px;
}

.detail-card {
  padding: 24px;
  position: sticky;
  top: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0;
}

.detail-grid dt {
  color: var(--muted);
  font-size: 12px;
}

.detail-grid dd {
  margin: 6px 0 0;
}

.detail-html {
  border-top: 1px solid var(--line);
  padding-top: 16px;
  line-height: 1.75;
}

.detail-html img {
  max-width: 100%;
  border-radius: 12px;
}

.detail-html table {
  max-width: 100%;
  display: block;
  overflow-x: auto;
}

.state {
  padding: 24px;
  color: var(--muted);
}

.state.error {
  color: #a13333;
  border-color: rgba(161, 51, 51, 0.35);
}

.sync-button,
.ghost,
.open-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  cursor: pointer;
}

.ghost {
  background: transparent;
  color: var(--accent);
}

.job-chip {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(46, 106, 87, 0.12);
  color: var(--accent-2);
  font-size: 13px;
}

.load-more-wrap {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

@media (max-width: 980px) {
  .toolbar-grid,
  .stats-grid,
  .content-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .hero-inner {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-actions {
    justify-items: start;
  }

  .detail-card {
    position: static;
  }
}
</style>
