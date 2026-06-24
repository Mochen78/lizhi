<template>
  <div class="admin-page">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-logo" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
            <path d="M145.1,102.2 Q152.0,112.0 145.1,121.8 Q148.0,133.4 138.2,139.8 Q136.8,151.6 125.6,153.6 Q119.9,163.7 109.0,161.0 Q100.0,168.0 91.0,161.0 Q80.1,163.7 74.4,153.6 Q63.2,151.6 61.8,139.8 Q52.0,133.4 54.9,121.8 Q48.0,112.0 54.9,102.2 Q52.0,90.6 61.8,84.2 Q63.2,72.4 74.4,70.4 Q80.1,60.3 91.0,63.0 Q100.0,56.0 109.0,63.0 Q119.9,60.3 125.6,70.4 Q136.8,72.4 138.2,84.2 Q148.0,90.6 145.1,102.2 Z" fill="#E53935"/>
            <g fill="#C62828" opacity="0.3">
              <circle cx="96" cy="78" r="2.5"/><circle cx="110" cy="78" r="2.5"/><circle cx="75" cy="92" r="2.5"/><circle cx="89" cy="92" r="2.5"/><circle cx="103" cy="92" r="2.5"/><circle cx="117" cy="92" r="2.5"/><circle cx="68" cy="106" r="2.5"/><circle cx="82" cy="106" r="2.5"/><circle cx="96" cy="106" r="2.5"/><circle cx="110" cy="106" r="2.5"/><circle cx="124" cy="106" r="2.5"/><circle cx="75" cy="120" r="2.5"/><circle cx="89" cy="120" r="2.5"/><circle cx="103" cy="120" r="2.5"/><circle cx="117" cy="120" r="2.5"/><circle cx="131" cy="120" r="2.5"/><circle cx="82" cy="134" r="2.5"/><circle cx="96" cy="134" r="2.5"/><circle cx="110" cy="134" r="2.5"/><circle cx="124" cy="134" r="2.5"/>
            </g>
            <path d="M100 62 C99 48 101 36 99 24" stroke="#2E7D32" stroke-width="3" fill="none" stroke-linecap="round"/>
            <path d="M99 28 C89 16 74 12 64 18 C74 22 89 26 99 28Z" fill="#43A047"/>
          </svg>
        </div>
        <div>
          <strong>荔知</strong>
          <small>后台状态看板</small>
        </div>
      </div>

      <nav class="sidebar-nav" aria-label="后台状态导航">
        <a v-for="item in navItems" :key="item.id" :href="'#' + item.id" :class="{ active: activeView === 'dashboard' && activeSection === item.id }" @click.prevent="scrollTo(item.id)">
          {{ item.label }}
        </a>
      </nav>

      <div class="sidebar-module">
        <span class="sidebar-module-label">反馈管理</span>
        <a href="#" :class="{ active: activeView === 'feedback' }" @click.prevent="goToFeedback">用户反馈</a>
      </div>

      <div class="sidebar-footer">
        <span class="conn-dot" :class="healthTone"></span>
        <span>{{ healthShortLabel }}</span>
      </div>
    </aside>

    <main class="main">
      <header class="page-header">
        <div>
          <h1>{{ activeView === 'feedback' ? '用户反馈管理' : '荔知后台状态看板' }}</h1>
          <p>{{ activeView === 'feedback' ? '用户对内容的反馈记录与统计' : '真实 API 数据，每 30 秒自动刷新' }}</p>
        </div>
        <div class="header-meta">
          <span class="status-badge" :class="healthTone"><span class="dot"></span>{{ healthLabel }}</span>
          <span>{{ lastUpdatedLabel }}</span>
        </div>
      </header>

      <div class="content">
        <template v-if="activeView === 'dashboard'">
        <section id="overview" class="section">
          <div class="section-title">总览</div>
          <div class="kpi-row">
            <article class="card">
              <div class="card-label">总文章</div>
              <div class="card-value">{{ formatNumber(ingestion?.posts_total) }}</div>
              <p class="card-help">数据库中已入库的文章总数。</p>
            </article>
            <article class="card">
              <div class="card-label">等待处理</div>
              <div class="card-value warning">{{ formatNumber(queue?.pending) }}</div>
              <p class="card-help">队列中还没开始执行的任务。</p>
            </article>
            <article class="card">
              <div class="card-label">启用来源</div>
              <div class="card-value info">{{ formatNumber(ingestion?.sources_enabled) }}</div>
              <p class="card-help">当前会参与自动采集的公众号来源。</p>
            </article>
            <article class="card">
              <div class="card-label">支持数</div>
              <div class="card-value danger">{{ formatNumber(support?.count) }}</div>
              <p class="card-help">前台用户点击“加荔枝”的累计次数。</p>
            </article>
          </div>

          <div class="status-grid">
            <article class="card status-card">
              <h3>服务状态</h3>
              <div class="status-lines">
                <div><span>后端服务</span><strong>{{ healthLabel }}</strong></div>
                <div><span>数据库</span><strong>{{ health?.database === 'ok' ? '正常' : '异常或未知' }}</strong></div>
                <div><span>上游配置</span><strong>{{ health?.upstream_configured ? '已配置' : '未配置' }}</strong></div>
              </div>
            </article>
            <article class="card status-card">
              <h3>最近成功同步</h3>
              <div v-if="ingestion?.last_successful_sync" class="status-lines">
                <div><span>同步编号</span><strong>#{{ ingestion.last_successful_sync.id }}</strong></div>
                <div><span>完成时间</span><strong>{{ formatDateTime(ingestion.last_successful_sync.finished_at) }}</strong></div>
                <div><span>结果</span><strong>新增 {{ ingestion.last_successful_sync.posts_inserted }}，更新 {{ ingestion.last_successful_sync.posts_updated }}</strong></div>
              </div>
              <p v-else class="empty">暂无成功同步记录。</p>
            </article>
          </div>
        </section>

        <section id="queue" class="section">
          <div class="section-title">队列</div>
          <div class="card table-card">
            <table class="data-table queue-table">
              <colgroup>
                <col class="queue-status-col">
                <col class="queue-help-col">
                <col class="queue-number-col">
              </colgroup>
              <thead>
                <tr><th>状态</th><th>含义</th><th class="num">数量</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in queueRows" :key="row.key">
                  <td><span class="badge" :class="row.badge">{{ row.label }}</span></td>
                  <td>{{ row.help }}</td>
                  <td class="num">{{ formatNumber(row.count) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="pipeline" class="section">
          <div class="section-title">处理管线</div>
          <div class="card table-card">
            <table class="data-table pipeline-table">
              <colgroup>
                <col class="pipeline-type-col">
                <col class="pipeline-number-col">
                <col class="pipeline-number-col">
                <col class="pipeline-number-col">
                <col class="pipeline-number-col">
              </colgroup>
              <thead>
                <tr>
                  <th>任务类型</th>
                  <th class="num">等待中</th>
                  <th class="num">运行中</th>
                  <th class="num">已完成</th>
                  <th class="num">异常</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in pipelineRows" :key="row.type">
                  <td>{{ jobTypeLabel(row.type) }}</td>
                  <td class="num">{{ formatNumber(row.pending) }}</td>
                  <td class="num">{{ formatNumber(row.running) }}</td>
                  <td class="num">{{ formatNumber(row.succeeded) }}</td>
                  <td class="num">{{ formatNumber(row.failed + row.dead + row.cancelled) }}</td>
                </tr>
                <tr v-if="!pipelineRows.length"><td colspan="5" class="empty">暂无任务管线数据。</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="activity" class="section">
          <div class="section-title">24小时新增</div>
          <div class="card">
            <div v-if="hourlyRows.length" class="bar-chart">
              <div v-for="row in hourlyRows" :key="row.hour" class="bar-row">
                <span class="bar-label">{{ row.label }}</span>
                <div class="bar-track"><div class="bar-fill" :style="{ width: row.width + '%' }"></div></div>
                <span class="bar-count">{{ row.inserted }}</span>
              </div>
            </div>
            <p v-else class="empty">最近 24 小时没有新增文章。若上游确实有新内容，需要检查刷新来源和同步文章任务。</p>
          </div>
        </section>

        <section id="sources" class="section">
          <div class="section-title">来源</div>
          <div class="card table-card">
            <table class="data-table">
              <thead>
                <tr><th style="width: 72px;">排名</th><th>来源名称</th><th class="num">24小时新增</th></tr>
              </thead>
              <tbody>
                <tr v-for="(source, index) in topSources" :key="source.source_name">
                  <td class="rank">#{{ index + 1 }}</td>
                  <td>{{ source.source_name }}</td>
                  <td class="num">{{ formatNumber(source.inserted) }}</td>
                </tr>
                <tr v-if="!topSources.length"><td colspan="3" class="empty">最近 24 小时暂无来源新增。</td></tr>
              </tbody>
            </table>
          </div>
       </section>

        </template>
        <template v-if="activeView === 'feedback'">
          <button class="fb-back-btn" @click="backToDashboard">← 返回看板</button>
        <section id="feedback" class="section fb-section">
          <div class="section-title fb-section-title">用户反馈</div>

          <!-- Summary by category -->
          <div class="card table-card">
            <div class="card-head">按分类汇总</div>
            <table class="data-table">
              <thead>
                <tr><th>分类</th><th class="num">有用</th><th class="num">没用</th><th class="num">反馈</th><th class="num">合计</th><th class="fb-reason-col">主要原因</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in feedbackSummary" :key="item.category">
                  <td>{{ categoryLabel(item.category) }}</td>
                  <td class="num fb-useful">{{ formatNumber(item.useful) }}</td>
                  <td class="num fb-useless">{{ formatNumber(item.useless) }}</td>
                  <td class="num">{{ formatNumber(item.feedback) }}</td>
                  <td class="num">{{ formatNumber(item.useful + item.useless + item.feedback) }}</td>
                  <td class="fb-reason-cell">{{ topReason(item.reasons) }}</td>
                </tr>
                <tr v-if="!feedbackSummary.length"><td colspan="6" class="empty">暂无反馈数据。</td></tr>
              </tbody>
              <tfoot v-if="feedbackSummary.length">
                <tr class="fb-total-row">
                  <td>总计</td>
                  <td class="num fb-useful">{{ formatNumber(feedbackTotals.useful) }}</td>
                  <td class="num fb-useless">{{ formatNumber(feedbackTotals.useless) }}</td>
                  <td class="num">{{ formatNumber(feedbackTotals.feedback) }}</td>
                  <td class="num">{{ formatNumber(feedbackTotals.total) }}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Recent feedback with filters + pagination -->
          <div class="card table-card fb-recent-card">
            <div class="card-head fb-recent-head">
              <span>最近反馈</span>
              <span class="fb-total-count">共 {{ feedbackFilteredTotal }} 条</span>
            </div>
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width: 130px;">时间</th>
                  <th style="width: 92px;" class="fb-filter-th">
                    分类
                    <button class="fb-filter-arrow" :class="{ on: feedbackCatFilter }" @click="feedbackCatOpen = !feedbackCatOpen">{{ feedbackCatFilter ? categoryLabel(feedbackCatFilter) : '全部' }} ▾</button>
                    <div class="fb-filter-menu" v-if="feedbackCatOpen" @click.stop>
                      <button :class="{ sel: !feedbackCatFilter }" @click="setFeedbackCatFilter('')">全部</button>
                      <button v-for="cat in CATEGORY_KEYS" :key="cat" :class="{ sel: feedbackCatFilter === cat }" @click="setFeedbackCatFilter(cat)">{{ categoryLabel(cat) }}</button>
                    </div>
                  </th>
                  <th style="width: 82px;" class="fb-filter-th">
                    类型
                    <button class="fb-filter-arrow" :class="{ on: feedbackVoteFilter }" @click="feedbackFilterOpen = !feedbackFilterOpen">{{ feedbackVoteFilter ? voteLabel(feedbackVoteFilter) : '全部' }} ▾</button>
                    <div class="fb-filter-menu" v-if="feedbackFilterOpen" @click.stop>
                      <button :class="{ sel: !feedbackVoteFilter }" @click="setFeedbackFilter('')">全部</button>
                      <button :class="{ sel: feedbackVoteFilter === 'useful' }" @click="setFeedbackFilter('useful')">有用</button>
                      <button :class="{ sel: feedbackVoteFilter === 'useless' }" @click="setFeedbackFilter('useless')">没用</button>
                      <button :class="{ sel: feedbackVoteFilter === 'feedback' }" @click="setFeedbackFilter('feedback')">反馈</button>
                    </div>
                  </th>
                 <th>文章</th>
                 <th style="width: 90px;">原因</th>
                 <th>内容</th>
                 <th style="width: 52px;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedFeedbackRecent" :key="item.id">
                  <td>{{ formatDateTime(item.created_at) }}</td>
                  <td><span class="badge badge-gray">{{ categoryLabel(item.post_category) || '-' }}</span></td>
                  <td><span class="badge" :class="voteBadgeClass(item.vote)">{{ voteLabel(item.vote) }}</span></td>
                  <td class="fb-post-cell">
                    <a v-if="item.post_url" :href="item.post_url" target="_blank" rel="noreferrer" class="fb-post-title">{{ item.post_title || '查看原文' }}</a>
                    <span v-else class="fb-post-title muted">{{ item.post_title || '-' }}</span>
                    <p v-if="item.post_summary" class="fb-post-summary">{{ item.post_summary }}</p>
                    <div v-if="item.source_name" class="fb-post-source">来源：{{ item.source_name }}</div>
                  </td>
                  <td>{{ reasonLabel(item.reason) || '-' }}</td>
                  <td class="fb-comment-cell">{{ item.comment || '-' }}</td>
                  <td><button class="fb-delete-btn" title="删除此记录" @click="deleteFeedbackRecord(item)">✕</button></td>
                </tr>
                <tr v-if="!paginatedFeedbackRecent.length"><td colspan="7" class="empty">暂无反馈记录。</td></tr>
              </tbody>
            </table>
            <div class="fb-pagination" v-if="feedbackTotalPages > 1">
              <button :disabled="feedbackPage === 1" @click="feedbackPage = 1">«</button>
              <button :disabled="feedbackPage === 1" @click="feedbackPage--">‹</button>
              <button v-for="p in feedbackPageNumbers" :key="p" :class="{ active: p === feedbackPage }" @click="feedbackPage = p">{{ p }}</button>
              <button :disabled="feedbackPage === feedbackTotalPages" @click="feedbackPage++">›</button>
              <button :disabled="feedbackPage === feedbackTotalPages" @click="feedbackPage = feedbackTotalPages">»</button>
            </div>
          </div>
        </section>

        </template>
        <template v-if="activeView === 'dashboard'">
        <section id="content" class="section">
          <div class="section-title">内容分布</div>
          <div class="stats-row">
            <article class="card">
              <h3>机会性质</h3>
              <div class="stat-list">
                <div v-for="item in statPairs(categories?.content_type_stats, contentTypeLabel)" :key="item.key" class="stat-item">
                  <span>
                    {{ item.label }}
                    <small>{{ contentTypeHelp(item.key) }}</small>
                  </span>
                  <strong>{{ formatNumber(item.value) }}</strong>
                </div>
                <p v-if="!statPairs(categories?.content_type_stats).length" class="empty">暂无数据</p>
              </div>
            </article>
            <article class="card">
              <h3>当前可参与性</h3>
              <div class="stat-list">
                <div v-for="item in statPairs(categories?.participation_stats, participationLabel)" :key="item.key" class="stat-item">
                  <span>
                    {{ item.label }}
                    <small>{{ participationHelp(item.key) }}</small>
                  </span>
                  <strong>{{ formatNumber(item.value) }}</strong>
                </div>
                <p v-if="!statPairs(categories?.participation_stats).length" class="empty">暂无数据</p>
              </div>
            </article>
            <article class="card">
              <h3>时间状态</h3>
              <div class="stat-list">
                <div v-for="item in statPairs(categories?.time_status_stats, timeStatusLabel)" :key="item.key" class="stat-item">
                  <span>
                    {{ item.label }}
                    <small>{{ timeStatusHelp(item.key) }}</small>
                  </span>
                  <strong>{{ formatNumber(item.value) }}</strong>
                </div>
                <p v-if="!statPairs(categories?.time_status_stats).length" class="empty">暂无数据</p>
              </div>
              <div v-if="statPairs(categories?.time_unknown_breakdown).length" class="stat-breakdown">
                <h4>未识别时间原因</h4>
                <div v-for="item in statPairs(categories?.time_unknown_breakdown, unknownTimeReasonLabel)" :key="item.key" class="stat-item compact">
                  <span>
                    {{ item.label }}
                    <small>{{ unknownTimeReasonHelp(item.key) }}</small>
                  </span>
                  <strong>{{ formatNumber(item.value) }}</strong>
                </div>
              </div>
            </article>
          </div>
        </section>

        <section id="guide" class="section">
          <div class="section-title">使用说明</div>
          <div class="guide-grid">
            <article class="card guide-card">
              <h3>怎么用</h3>
              <ol>
                <li>先看“服务状态”和“等待处理”：确认后端、数据库和队列是否正常。</li>
                <li>再看“处理管线”：判断是刷新来源、同步文章、抓取正文还是 LLM 处理卡住。</li>
                <li>最后看“24小时新增”和“来源”：确认系统有没有稳定拿到新文章，以及主要来自哪些公众号。</li>
              </ol>
            </article>
            <article class="card guide-card">
              <h3>指标含义</h3>
              <ul>
                <li><strong>总文章</strong>：数据库里已经保存的文章数量，不等于首页默认可见机会数。</li>
                <li><strong>等待中</strong>：还没被 worker 领取的任务，持续上涨说明处理速度不够。</li>
                <li><strong>运行中</strong>：worker 正在处理的任务，长期不变可能是任务卡住。</li>
                <li><strong>失败终止</strong>：重试后仍失败的任务，需要看日志或上游内容是否失效。</li>
                <li><strong>最近成功同步</strong>：最近一次成功写入同步审计的时间和新增/更新结果。</li>
              </ul>
            </article>
            <article class="card guide-card">
              <h3>监控建议</h3>
              <ul>
                <li>如果 24 小时无新增，但公众号上游有新文章，优先检查“刷新来源”和“同步文章”。</li>
                <li>如果“抓取正文”积压很多，说明正文爬取速度或上游访问稳定性需要关注。</li>
                <li>如果“LLM处理”积压很多，说明 AI 处理速度、开关或额度可能是瓶颈。</li>
                <li>公网只需要访问 <code>80 /api/*</code>；<code>8002</code> 是本机后端端口，不应公网开放。</li>
              </ul>
            </article>
          </div>
          <article class="card guide-card glossary-card">
            <h3>内容分布怎么看</h3>
            <div class="glossary-grid">
              <div>
                <h4>机会性质</h4>
                <p>回答“这篇文章本质上是不是一个机会”。<strong>明确机会</strong>通常是报名、招募、比赛、活动等；<strong>参考信息</strong>偏通知、资讯或政策，可能有用但不一定要行动；<strong>未判定</strong>表示规则暂时没有足够信息归类。</p>
              </div>
              <div>
                <h4>当前可参与性</h4>
                <p>回答“用户现在还能不能参与”。<strong>现在可参与</strong>代表报名、投递或参加条件大概率仍有效；<strong>当前不可参与</strong>通常是已过期、结果公示、回顾或纯通知；<strong>信息不足</strong>常见于摘要太短、正文缺失或时间尚未提取。</p>
              </div>
              <div>
                <h4>时间状态</h4>
                <p><strong>未识别时间</strong>表示没有提取到活动开始或截止时间，它们会按发布时间参与排序；<strong>未开始/进行中/已过期</strong>来自活动时间和截止时间的结构化提取。</p>
              </div>
            </div>
          </article>
          <article class="card guide-card architecture-card">
            <h3>文章采集、筛选与处理架构</h3>
            <div ref="mermaidEl" class="mermaid-box"></div>
          </article>
        </section>

        <section v-if="errorMessage" class="section">
          <div class="card error-card">
            <strong>加载异常</strong>
            <span>{{ errorMessage }}</span>
          </div>
        </section>
        </template>
      </div>
    </main>
  </div>
</template>

<script>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import mermaid from 'mermaid'
import { getHealth, getIngestionHealth, getJobSummary, getPostCategories, getSupport } from '../api.js'
import { getFeedbackSummary, getFeedbackRecent, deleteFeedbackById } from '../api.js'

const POLL_MS = 30000

const JOB_TYPE_LABELS = {
  refresh_source: '刷新来源',
  sync_source_posts: '同步文章',
  fetch_content: '抓取正文',
  llm_post: 'LLM处理',
}

const CONTENT_TYPE_LABELS = {
  actionable: '明确机会',
  reference: '参考信息',
  non_actionable: '非机会内容',
  unknown: '未判定',
  campus_activity: '校园活动',
  lecture: '讲座论坛',
  volunteer: '志愿公益',
  competition: '学科竞赛',
  recruitment: '就业招聘',
  graduate_study: '升学留学',
  exam_certification: '考试考证',
  other: '其他',
}

const PARTICIPATION_LABELS = {
  participable: '现在可参与',
  non_participable: '当前不可参与',
  uncertain: '信息不足',
  open: '现在可参与',
  restricted: '有限制',
  informational: '仅信息',
  unknown: '未知',
}

const TIME_STATUS_LABELS = {
  undated: '未识别时间',
  upcoming: '未开始',
  ongoing: '进行中',
  deadline_soon: '即将截止',
  expired: '已过期',
  unknown: '未知',
}

const CONTENT_TYPE_HELP = {
  actionable: '文章本质是一个可报名、可参加或可投递的机会',
  reference: '文章有信息价值，但不一定构成一个可参与机会',
  non_actionable: '回顾、结果、公示、介绍等不构成机会的内容',
  unknown: '规则暂时没有足够信息判断机会性质',
}

const PARTICIPATION_HELP = {
  participable: '从时间和文本看，用户当前大概率还能报名、投递或参加',
  non_participable: '已过期、不可报名，或本身只是回顾/公示/通知',
  uncertain: '正文、时间或参与条件不足，暂时无法判断当前能否参与',
}

const TIME_STATUS_HELP = {
  undated: '未提取到活动开始或截止时间',
  upcoming: '关键时间还没到',
  ongoing: '活动时间范围内',
  deadline_soon: '截止时间接近',
  expired: '活动或截止时间已过',
  unknown: '时间信息不足',
}

const UNKNOWN_TIME_REASON_LABELS = {
  content_missing: '正文缺失',
  llm_waiting: '等待 LLM',
  llm_failed: 'LLM 失败',
  processed_no_time: '已处理但无时间',
  other: '其他原因',
}

const UNKNOWN_TIME_REASON_HELP = {
  content_missing: '正文还没抓到或抓取失败，时间通常藏在正文里',
  llm_waiting: '正文已准备好，但还没完成结构化时间提取',
  llm_failed: 'LLM 处理重试后失败，需要看失败任务或日志',
  processed_no_time: '已经处理过，但正文里没有明确活动开始或截止时间',
  other: '状态不在常规分类中，需要进一步排查',
}

const PIPELINE_MERMAID = `flowchart LR
  Timer["定时器<br/>systemd timer"] --> Enqueue["入队器<br/>enqueue_refresh_jobs"]
  Enqueue --> Queue[("job_queue<br/>数据库队列")]
  Queue --> Refresh["refresh_worker<br/>刷新来源 / 同步文章"]
  Refresh --> Upstream["WeRSS / 公众号源"]
  Upstream --> Prescreen["规则初筛<br/>过滤广告、回顾、乱码"]
  Prescreen -->|通过| Store["入库<br/>posts / projections"]
  Prescreen -->|过滤| Discard["丢弃记录<br/>discarded_posts"]
  Store -->|缺正文| Queue
  Queue --> Content["content_worker<br/>抓取正文"]
  Content --> Store
  Store -->|需要结构化| Queue
  Queue --> LLM["llm_worker<br/>标题、摘要、分类、时间"]
  LLM --> Projection["更新投影<br/>机会性质 / 当前可参与性 / 时间状态"]
  Projection --> API["/api/posts<br/>/api/jobs/ingestion-health"]
  API --> Dashboard["后台看板 / 前台机会列表"]`

export default {
  name: 'AdminStatus',
  setup() {
    const health = ref(null)
    const queue = ref(null)
    const ingestion = ref(null)
    const categories = ref(null)
    const support = ref(null)
    const feedbackSummary = ref([])
    const feedbackRecent = ref([])
    const feedbackVoteFilter = ref('')
    const feedbackFilterOpen = ref(false)
    const feedbackCatFilter = ref('')
    const feedbackCatOpen = ref(false)
    const feedbackPage = ref(1)
    const FEEDBACK_PAGE_SIZE = 20
    const CATEGORY_KEYS = ['campus_activity', 'competition', 'volunteer', 'exam_certification', 'recruitment', 'lecture', 'graduate_study', 'other']
    const CATEGORY_LABELS = {
      campus_activity: '校园活动', competition: '学科竞赛', volunteer: '志愿公益',
      exam_certification: '考试考证', recruitment: '就业招聘', lecture: '讲座论坛',
      graduate_study: '升学留学', other: '其他',
    }
    const errorMessage = ref('')
    const lastUpdated = ref(null)
    const activeSection = ref('overview')
    const activeView = ref('dashboard')
    const mermaidEl = ref(null)
    let pollTimer = null
    let observer = null

    const navItems = [
      { id: 'overview', label: '总览' },
      { id: 'queue', label: '队列' },
      { id: 'pipeline', label: '处理管线' },
      { id: 'activity', label: '24小时新增' },
     { id: 'sources', label: '来源' },
     { id: 'content', label: '内容分布' },
     { id: 'guide', label: '使用说明' },
   ]

    const healthTone = computed(() => {
      if (!health.value) return 'warn'
      if (health.value.status === 'ok') return 'ok'
      if (health.value.status === 'degraded') return 'warn'
      return 'bad'
    })
    const healthLabel = computed(() => {
      if (!health.value) return '加载中'
      if (health.value.status === 'ok') return '运行正常'
      if (health.value.status === 'degraded') return '部分降级'
      return '异常'
    })
    const healthShortLabel = computed(() => {
      if (!health.value) return '连接中'
      return `数据库：${health.value.database === 'ok' ? '正常' : '异常'}`
    })
    const lastUpdatedLabel = computed(() => {
      if (!lastUpdated.value) return '尚未刷新'
      return `更新 ${lastUpdated.value.toLocaleTimeString('zh-CN', { hour12: false })}`
    })

    const queueRows = computed(() => [
      { key: 'pending', label: '等待中', help: '已入队但尚未被 worker 领取', count: queue.value?.pending || 0, badge: 'badge-amber' },
      { key: 'running', label: '运行中', help: 'worker 正在处理', count: queue.value?.running || 0, badge: 'badge-blue' },
      { key: 'succeeded', label: '已完成', help: '处理成功并已记录结果', count: queue.value?.succeeded || 0, badge: 'badge-green' },
      { key: 'failed', label: '失败待重试', help: '失败但还没达到最大重试次数', count: queue.value?.failed || 0, badge: 'badge-red' },
      { key: 'dead', label: '失败终止', help: '达到最大重试次数后停止', count: queue.value?.dead || 0, badge: 'badge-gray' },
      { key: 'cancelled', label: '已取消', help: '被治理逻辑取消或跳过', count: queue.value?.cancelled || 0, badge: 'badge-gray' },
    ])

    const pipelineRows = computed(() => {
      const rows = {}
      for (const item of ingestion.value?.queue_by_type_status || []) {
        const type = item.job_type || 'unknown'
        const status = item.status || 'pending'
        if (!rows[type]) rows[type] = { type, pending: 0, running: 0, succeeded: 0, failed: 0, dead: 0, cancelled: 0 }
        if (Object.prototype.hasOwnProperty.call(rows[type], status)) rows[type][status] += Number(item.count || 0)
      }
      return Object.values(rows).sort((a, b) => jobTypeLabel(a.type).localeCompare(jobTypeLabel(b.type), 'zh-CN'))
    })

    const hourlyRows = computed(() => {
      const rows = ingestion.value?.posts_inserted_by_hour_24h || []
      const max = Math.max(1, ...rows.map((row) => Number(row.inserted || 0)))
      return rows.map((row) => {
        const raw = String(row.hour || '')
        const label = raw.includes('T') ? raw.split('T')[1].slice(0, 5) : raw.slice(-5)
        const inserted = Number(row.inserted || 0)
        return { hour: row.hour, label, inserted, width: Math.max(2, Math.round((inserted / max) * 100)) }
      })
    })

    const topSources = computed(() => (ingestion.value?.top_sources_inserted_24h || []).slice(0, 10))

    const filteredFeedbackRecent = computed(() => {
      let list = feedbackRecent.value
      if (feedbackVoteFilter.value) list = list.filter((item) => item.vote === feedbackVoteFilter.value)
      if (feedbackCatFilter.value) list = list.filter((item) => item.post_category === feedbackCatFilter.value)
      return list
    })

    const feedbackFilteredTotal = computed(() => filteredFeedbackRecent.value.length)
    const feedbackTotalPages = computed(() => Math.max(1, Math.ceil(feedbackFilteredTotal.value / FEEDBACK_PAGE_SIZE)))
    const paginatedFeedbackRecent = computed(() => {
      const start = (feedbackPage.value - 1) * FEEDBACK_PAGE_SIZE
      return filteredFeedbackRecent.value.slice(start, start + FEEDBACK_PAGE_SIZE)
    })
    const feedbackPageNumbers = computed(() => {
      const total = feedbackTotalPages.value
      const cur = feedbackPage.value
      const pages = []
      let startPage = Math.max(1, cur - 2)
      const endPage = Math.min(total, startPage + 4)
      startPage = Math.max(1, endPage - 4)
      for (let p = startPage; p <= endPage; p++) pages.push(p)
      return pages
    })

    const feedbackTotals = computed(() => {
      const totals = { useful: 0, useless: 0, feedback: 0, total: 0 }
      for (const item of feedbackSummary.value) {
        totals.useful += item.useful || 0
        totals.useless += item.useless || 0
        totals.feedback += item.feedback || 0
      }
      totals.total = totals.useful + totals.useless + totals.feedback
      return totals
    })

    function setFeedbackFilter(vote) {
      feedbackVoteFilter.value = vote
      feedbackFilterOpen.value = false
      feedbackPage.value = 1
    }
    function setFeedbackCatFilter(cat) {
      feedbackCatFilter.value = cat
      feedbackCatOpen.value = false
      feedbackPage.value = 1
    }
    function categoryLabel(code) {
      return CATEGORY_LABELS[code] || code || ''
    }

    function onDocClick(event) {
      if (!event.target.closest('.fb-filter-th')) {
        feedbackFilterOpen.value = false
        feedbackCatOpen.value = false
      }
    }

    async function deleteFeedbackRecord(item) {
      if (!confirm(`确定删除这条反馈记录吗？\n类型：${voteLabel(item.vote)}${item.comment ? '\n内容：' + item.comment : ''}`)) return
      try {
        await deleteFeedbackById(item.id)
        feedbackRecent.value = feedbackRecent.value.filter((r) => r.id !== item.id)
        feedbackSummary.value = await getFeedbackSummary()
      } catch (e) {
        errorMessage.value = e?.response?.data?.detail || e?.message || '删除失败'
      }
    }

    async function loadAll() {
      const results = await Promise.allSettled([
        getHealth(),
        getJobSummary(),
        getIngestionHealth(),
        getPostCategories(),
      getSupport('admin-status-board'),
      getFeedbackSummary(),
      getFeedbackRecent(50),
    ])
      const [healthResult, queueResult, ingestionResult, categoriesResult, supportResult, feedbackSummaryResult, feedbackRecentResult] = results
      if (healthResult.status === 'fulfilled') health.value = healthResult.value
      if (queueResult.status === 'fulfilled') queue.value = queueResult.value
      if (ingestionResult.status === 'fulfilled') ingestion.value = ingestionResult.value
      if (categoriesResult.status === 'fulfilled') categories.value = categoriesResult.value
      if (supportResult.status === 'fulfilled') support.value = supportResult.value
      if (feedbackSummaryResult.status === 'fulfilled') feedbackSummary.value = feedbackSummaryResult.value
      if (feedbackRecentResult.status === 'fulfilled') feedbackRecent.value = feedbackRecentResult.value
      const rejected = results.find((result) => result.status === 'rejected')
      errorMessage.value = rejected ? (rejected.reason?.response?.data?.detail || rejected.reason?.message || '部分接口加载失败') : ''
      lastUpdated.value = new Date()
    }

    function scrollTo(id) {
      activeView.value = 'dashboard'
      nextTick(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        activeSection.value = id
      })
    }
    function goToFeedback() {
      activeView.value = 'feedback'
    }
    function backToDashboard() {
      activeView.value = 'dashboard'
      nextTick(() => {
        document.getElementById('overview')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    }
    function initScrollSpy() {
      observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) activeSection.value = entry.target.id
        }
      }, { rootMargin: '-90px 0px -65% 0px', threshold: 0 })
      for (const item of navItems) {
        const element = document.getElementById(item.id)
        if (element) observer.observe(element)
      }
    }
    function formatNumber(value) {
      const number = Number(value || 0)
      return Number.isFinite(number) ? number.toLocaleString('zh-CN') : '0'
    }
    function formatDateTime(value) {
      if (!value) return '暂无'
      const date = new Date(value)
      return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString('zh-CN', { hour12: false })
    }
    function statPairs(obj, labeler = (value) => value) {
      return Object.entries(obj || {})
        .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))
        .map(([key, value]) => ({ key, label: labeler(key), value }))
    }
    function jobTypeLabel(value) { return JOB_TYPE_LABELS[value] || String(value || '未知任务') }
    function contentTypeLabel(value) { return CONTENT_TYPE_LABELS[value] || String(value || '未知') }
    function participationLabel(value) { return PARTICIPATION_LABELS[value] || String(value || '未知') }
    function timeStatusLabel(value) { return TIME_STATUS_LABELS[value] || String(value || '未知') }
    function unknownTimeReasonLabel(value) { return UNKNOWN_TIME_REASON_LABELS[value] || String(value || '未知原因') }
    function contentTypeHelp(value) { return CONTENT_TYPE_HELP[value] || '保留后端原始分类值' }
    function participationHelp(value) { return PARTICIPATION_HELP[value] || '保留后端原始参与状态' }
    function timeStatusHelp(value) { return TIME_STATUS_HELP[value] || '保留后端原始时间状态' }
    function unknownTimeReasonHelp(value) { return UNKNOWN_TIME_REASON_HELP[value] || '保留后端原始原因' }
    const VOTE_LABELS = { useful: '有用', useless: '没用', feedback: '反馈' }
    const REASON_LABELS = {
      not_activity: '不是活动', expired: '已过期', wrong_category: '分类错了',
      other: '其他',
    }
    function voteLabel(value) { return VOTE_LABELS[value] || value || '' }
    function reasonLabel(value) { return REASON_LABELS[value] || value || '' }
    function topReason(reasons) {
      if (!reasons) return ''
      const entries = Object.entries(reasons).sort((a, b) => b[1] - a[1])
      return entries.length ? reasonLabel(entries[0][0]) : ''
    }
    function voteBadgeClass(vote) {
      if (vote === 'useful') return 'badge-green'
      if (vote === 'useless') return 'badge-red'
      return 'badge-blue'
    }
    async function renderMermaid() {
      if (!mermaidEl.value) return
      try {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          theme: 'base',
          themeVariables: {
            fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
            primaryColor: '#eff6ff',
            primaryTextColor: '#111827',
            primaryBorderColor: '#93c5fd',
            lineColor: '#64748b',
            secondaryColor: '#ecfdf5',
            tertiaryColor: '#fff7ed',
          },
        })
        const { svg } = await mermaid.render(`admin-pipeline-${Date.now()}`, PIPELINE_MERMAID)
        mermaidEl.value.innerHTML = svg
      } catch (error) {
        mermaidEl.value.innerHTML = '<p class="empty">架构图渲染失败，请刷新页面重试。</p>'
      }
    }

    onMounted(() => {
      loadAll()
      initScrollSpy()
      nextTick(renderMermaid)
      pollTimer = window.setInterval(loadAll, POLL_MS)
      document.addEventListener('click', onDocClick)
    })
    onUnmounted(() => {
      if (pollTimer) window.clearInterval(pollTimer)
      if (observer) observer.disconnect()
      document.removeEventListener('click', onDocClick)
    })

   return {
     navItems,
     activeSection,
     activeView,
     health,
     queue,
      ingestion,
      categories,
     support,
      feedbackSummary,
     feedbackRecent,
     feedbackVoteFilter,
     feedbackFilterOpen,
      feedbackCatFilter,
      feedbackCatOpen,
      feedbackPage,
     filteredFeedbackRecent,
      paginatedFeedbackRecent,
      feedbackFilteredTotal,
      feedbackTotalPages,
      feedbackPageNumbers,
      feedbackTotals,
      CATEGORY_KEYS,
      setFeedbackCatFilter,
      categoryLabel,
     setFeedbackFilter,
      deleteFeedbackRecord,
     errorMessage,
      mermaidEl,
      healthTone,
      healthLabel,
      healthShortLabel,
      lastUpdatedLabel,
      queueRows,
      pipelineRows,
      hourlyRows,
     topSources,
     scrollTo,
     goToFeedback,
     backToDashboard,
     formatNumber,
      formatDateTime,
      statPairs,
      jobTypeLabel,
      contentTypeLabel,
      participationLabel,
      timeStatusLabel,
      unknownTimeReasonLabel,
      contentTypeHelp,
      participationHelp,
     timeStatusHelp,
     unknownTimeReasonHelp,
     voteLabel,
     voteBadgeClass,
     reasonLabel,
      topReason,
   }
  },
}
</script>

<style scoped>
* { box-sizing: border-box; }

.admin-page {
  min-height: 100vh;
  background: #f9fafb;
  color: #111827;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 100;
  width: 216px;
  display: flex;
  flex-direction: column;
  background: #1f2937;
  color: #fff;
  overflow-y: auto;
}

.sidebar-brand {
  min-height: 76px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #374151;
}

.brand-logo {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  background: #111827;
  border: 1px solid #374151;
  flex: 0 0 auto;
}

.brand-logo svg { width: 34px; height: 34px; }
.sidebar-brand strong { display: block; font-size: 17px; line-height: 1.1; }
.sidebar-brand small { display: block; margin-top: 3px; color: #9ca3af; font-size: 12px; }

.sidebar-nav {
  flex: 1;
  padding: 8px 0;
}

.sidebar-nav a {
  display: block;
  min-height: 38px;
  padding: 10px 16px;
  border-left: 3px solid transparent;
  color: #d1d5db;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.sidebar-nav a:hover {
  background: #374151;
  color: #fff;
}

.sidebar-nav a.active {
  background: #111827;
  color: #fff;
  border-left-color: #3b82f6;
}

.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid #374151;
  color: #d1d5db;
  font-size: 12px;
}

.conn-dot,
.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 6px;
  background: #f59e0b;
  vertical-align: middle;
}

.conn-dot.ok,
.dot.ok,
.status-badge.ok .dot { background: #10b981; }
.conn-dot.bad,
.dot.bad,
.status-badge.bad .dot { background: #ef4444; }

.main {
  margin-left: 216px;
  min-height: 100vh;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.page-header h1 {
  margin: 0;
  font-size: 20px;
  line-height: 1.25;
}

.page-header p {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6b7280;
  font-size: 12px;
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #fde68a;
  background: #fffbeb;
  color: #b45309;
  font-weight: 700;
}

.status-badge.ok {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #047857;
}

.status-badge.bad {
  border-color: #fecaca;
  background: #fef2f2;
  color: #dc2626;
}

.content {
  padding: 24px;
}

.section {
  scroll-margin-top: 86px;
  margin-bottom: 26px;
}

.section-title {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  padding: 16px;
}

.card h3 {
  margin: 0 0 12px;
  font-size: 15px;
}

.card-label {
  margin-bottom: 8px;
  color: #9ca3af;
  font-size: 12px;
  font-weight: 800;
}

.card-value {
  color: #111827;
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.card-value.warning { color: #d97706; }
.card-value.danger { color: #dc2626; }
.card-value.info { color: #2563eb; }
.card-help {
  margin: 10px 0 0;
  color: #6b7280;
  font-size: 12px;
  line-height: 1.5;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.status-grid,
.stats-row,
.guide-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.stats-row,
.guide-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 0;
}

.status-lines {
  display: grid;
  gap: 10px;
}

.status-lines div,
.stat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-lines span,
.stat-item span {
  color: #6b7280;
}

.status-lines strong,
.stat-item strong {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.table-card {
  padding: 0;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 13px;
}

.data-table th {
  padding: 9px 12px;
  border-bottom: 1px solid #e5e7eb;
  border-left: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #6b7280;
  text-align: left;
  font-size: 12px;
  font-weight: 800;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f3f4f6;
  border-left: 1px solid #f3f4f6;
  color: #374151;
}

.data-table th:first-child,
.data-table td:first-child {
  border-left: 0;
}

.queue-status-col {
  width: 18%;
}

.queue-help-col {
  width: 64%;
}

.queue-number-col {
  width: 18%;
}

.pipeline-type-col {
  width: 26%;
}

.pipeline-number-col {
  width: 18.5%;
}

.data-table tr:last-child td {
  border-bottom: 0;
}

.num {
  text-align: center;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.badge {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 800;
}

.badge-amber { background: #fef3c7; color: #92400e; }
.badge-blue { background: #dbeafe; color: #1d4ed8; }
.badge-green { background: #d1fae5; color: #047857; }
.badge-red { background: #fee2e2; color: #b91c1c; }
.badge-gray { background: #f3f4f6; color: #4b5563; }

.bar-chart {
  display: grid;
  gap: 9px;
}

.bar-row {
  display: grid;
  grid-template-columns: 52px 1fr 52px;
  align-items: center;
  gap: 10px;
}

.bar-label,
.bar-count {
  color: #6b7280;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

.bar-count {
  text-align: right;
  font-weight: 700;
}

.bar-track {
  height: 12px;
  background: #e5e7eb;
}

.bar-fill {
  height: 100%;
  background: #2563eb;
}

.rank {
  color: #1d4ed8;
  font-weight: 800;
}

.stat-list {
  display: grid;
  gap: 9px;
}

.stat-item {
  align-items: flex-start;
}

.stat-item span {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
}

.stat-item small {
  color: #9ca3af;
  font-size: 12px;
  line-height: 1.45;
}

.stat-breakdown {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.stat-breakdown h4 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 14px;
}

.stat-item.compact {
  padding: 7px 0;
}

.guide-card ol,
.guide-card ul {
  margin: 0;
  padding-left: 20px;
  color: #374151;
  font-size: 13px;
  line-height: 1.75;
}

.guide-card code {
  color: #1d4ed8;
  font-family: Consolas, "Courier New", monospace;
}

.glossary-card,
.architecture-card {
  margin-top: 16px;
}

.glossary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.glossary-grid h4 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 14px;
}

.glossary-grid p {
  margin: 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.75;
}

.mermaid-box {
  width: 100%;
  min-height: 360px;
  overflow-x: auto;
  padding: 12px;
  border: 1px solid #e5e7eb;
  background: #fbfdff;
}

.mermaid-box :deep(svg) {
  display: block;
  max-width: none;
  min-width: 980px;
  margin: 0 auto;
}

.empty {
  color: #9ca3af;
  font-size: 13px;
}

.error-card {
  display: flex;
  gap: 10px;
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

@media (max-width: 1040px) {
  .kpi-row,
  .stats-row,
  .guide-grid,
  .glossary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .sidebar {
    position: static;
    width: 100%;
    height: auto;
  }

  .sidebar-nav {
    display: flex;
    overflow-x: auto;
    padding: 0;
  }

  .sidebar-nav a {
    flex: 0 0 auto;
    border-left: 0;
    border-bottom: 3px solid transparent;
  }

  .sidebar-nav a.active {
    border-left: 0;
    border-bottom-color: #3b82f6;
  }

  .sidebar-footer {
    display: none;
  }

  .main {
    margin-left: 0;
  }

  .page-header {
    position: static;
    align-items: flex-start;
    flex-direction: column;
  }

  .header-meta {
    white-space: normal;
    flex-wrap: wrap;
  }

  .content {
    padding: 16px;
  }

  .kpi-row,
  .status-grid,
  .stats-row,
  .guide-grid,
  .glossary-grid {
    grid-template-columns: 1fr;
  }

  .table-card {
    overflow-x: auto;
  }

    .data-table {
    min-width: 560px;
  }
}

/* === Feedback Section === */
.card-head {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 800;
}

.fb-reason-col { width: 120px; }
.fb-reason-cell { font-size: 12px; color: #6b7280; }
.fb-useful { color: #047857 !important; }
.fb-useless { color: #dc2626 !important; }

.fb-recent-card { margin-top: 16px; }
.fb-comment-cell { color: #4b5563; font-size: 12px; }

.fb-post-cell { min-width: 200px; max-width: 320px; }
.fb-post-title { display: inline-block; font-size: 13px; font-weight: 600; color: #1d4ed8; text-decoration: none; }
.fb-post-title:hover { text-decoration: underline; }
.fb-post-title.muted { color: #6b7280; font-weight: 500; }
.fb-post-summary { margin: 4px 0 0; font-size: 12px; color: #6b7280; line-height: 1.55; }

/* Type filter dropdown on the 最近反馈 table */
.fb-filter-th { position: relative; white-space: nowrap; }
.fb-filter-arrow {
  margin-left: 6px; padding: 2px 8px; border: 1px solid #d1d5db; border-radius: 6px;
  background: #fff; color: #374151; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.fb-filter-arrow:hover { border-color: #6b7280; }
.fb-filter-arrow.on { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }
.fb-filter-menu {
  position: absolute; top: 100%; left: 0; z-index: 50; margin-top: 4px;
  background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  display: flex; flex-direction: column; min-width: 96px; overflow: hidden;
}
.fb-filter-menu button {
  padding: 8px 12px; border: none; background: #fff; color: #374151;
  font-size: 12px; text-align: left; cursor: pointer;
}
.fb-filter-menu button:hover { background: #f3f4f6; }
.fb-filter-menu button.sel { background: #eff6ff; color: #1d4ed8; font-weight: 700; }

.fb-post-source { margin-top: 4px; text-align: right; font-size: 11px; color: #9ca3af; }

.fb-recent-head { display: flex; justify-content: space-between; align-items: center; }
.fb-total-count { font-size: 12px; font-weight: 600; color: #6b7280; }

.fb-total-row td { font-weight: 800; background: #f9fafb; border-top: 2px solid #e5e7eb; }

.fb-section { border-top: 3px solid #e5e7eb; padding-top: 8px; margin-top: 8px; }
.fb-section-title { padding-bottom: 4px; }

.fb-pagination { display: flex; gap: 4px; justify-content: center; padding: 12px 0 4px; flex-wrap: wrap; }
.fb-pagination button {
  min-width: 32px; height: 32px; border: 1px solid #d1d5db; border-radius: 6px;
  background: #fff; color: #374151; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.fb-pagination button:hover:not(:disabled) { border-color: #6b7280; background: #f9fafb; }
.fb-pagination button:disabled { opacity: 0.4; cursor: default; }
.fb-pagination button.active { border-color: #1d4ed8; background: #1d4ed8; color: #fff; }

.fb-delete-btn {
  width: 28px; height: 28px; border: 1px solid #fecaca; border-radius: 6px;
  background: #fff; color: #dc2626; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.15s;
}
.fb-delete-btn:hover { background: #dc2626; color: #fff; border-color: #dc2626; }

.fb-back-btn {
  display: inline-flex; align-items: center; gap: 4px; margin-bottom: 16px;
  padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px;
  background: #fff; color: #374151; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.fb-back-btn:hover { border-color: #1f2937; background: #f9fafb; }

.sidebar-module { padding: 12px 16px; border-top: 1px solid #374151; }
.sidebar-module-label { display: block; font-size: 10px; color: #9ca3af; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.sidebar-module a {
  display: block; padding: 8px 10px; border-radius: 6px; color: #d1d5db; text-decoration: none;
  font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.sidebar-module a:hover { background: #374151; color: #fff; }
.sidebar-module a.active { background: #1d4ed8; color: #fff; }
</style>
