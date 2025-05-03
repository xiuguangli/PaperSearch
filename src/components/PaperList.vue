<template>
  <div>
    <!-- 统一容器：包含过滤器、搜索和结果区域 -->
    <div class="filter-container">
      <table class="filter-table">
        <tbody>
          <!-- 第一行：过滤器和搜索区域 -->
          <tr>
            <td style="width: 25%;">
              <el-select v-model="selectedConference" @change="handleConferenceChange" placeholder="选择会议" class="full-width-select">
                <el-option v-for="conference in conferences" :key="conference" :label="conference" :value="conference"></el-option>
              </el-select>
            </td>
            <td style="width: 25%;">
              <el-select v-model="selectedYear" @change="loadPapers" placeholder="选择年份" class="full-width-select">
                <el-option v-for="year in availableYears" :key="year" :label="year" :value="year"></el-option>
              </el-select>
            </td>
            <td style="width: 25%;">
              <el-input v-model="searchQuery" @input="handleSearch" placeholder="在标题中搜索" clearable @clear="searchQuery = ''; handleSearch()">
                <template #prefix><el-icon><el-icon-search /></el-icon></template>
              </el-input>
            </td>
            <td style="width: 25%; padding-right: var(--spacing-medium);">
              <el-input v-model="abstractSearchQuery" @input="handleSearch" placeholder="在摘要中搜索" clearable @clear="abstractSearchQuery = ''; handleSearch()">
                <template #prefix><el-icon><el-icon-search /></el-icon></template>
              </el-input>
            </td>
          </tr>

          <!-- 第二行：会议信息 -->
          <tr v-if="paperData && !loading && !error">
            <td colspan="4">
              <h2 class="conference-title">{{ selectedConference }} {{ selectedYear }} - 共 {{ paperData.total_papers || papers.length }} 篇论文</h2>
            </td>
          </tr>

          <!-- 第三行：搜索结果信息、排序控制和分页控制 -->
          <tr v-if="paperData && !loading && !error">
            <td colspan="4">
              <span class="search-result-text">搜索结果: 找到 {{ filteredPapers.length }} 篇匹配论文</span>
            </td>
          </tr>

          <!-- 第四行：排序控制和分页控制 -->
          <tr>
            <td colspan="3" style="width: 75%; text-align: left; padding-top: 15px; padding-bottom: 15px;">
              <div class="sort-controls">
                <div class="sort-buttons">
                  <el-radio-group v-model="sortBy" @change="handleSortChange" size="small">
                    <el-radio-button value="order">默认排序</el-radio-button>
                    <el-radio-button value="title">标题排序</el-radio-button>
                  </el-radio-group>
                  <el-button @click="toggleSortDirection" :title="sortDirection === 'asc' ? '升序' : '降序'" class="sort-direction-button">
                    <span>{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                  </el-button>
                </div>
              </div>
            </td>
            <td colspan="1" style="width: 25%; padding-right: var(--spacing-medium); padding-top: 15px; padding-bottom: 15px;">
              <div class="pagination-controls">
                <span class="total-count">共 {{ filteredPapers.length }} 篇</span>
                <el-select v-model="pageSize" @change="handleSizeChange" size="small" class="page-size-select">
                  <el-option :value="10" label="10 篇/页" />
                  <el-option :value="50" label="50 篇/页" />
                  <el-option :value="100" label="100 篇/页" />
                  <el-option :value="filteredPapers.length" label="全部显示" />
                </el-select>
              </div>
            </td>
          </tr>

          <!-- 第五行（可选）：标题关键词 -->
          <tr v-if="searchKeywords.length > 0">
            <td colspan="4">
              <div class="keyword-line">
                <span class="keyword-label">标题关键词:</span>
                <div class="keyword-content">
                  <span v-for="(keyword, i) in searchKeywords" :key="i">
                    {{ keyword }}{{ i < searchKeywords.length - 1 ? ', ' : '' }}
                  </span>
                </div>
              </div>
            </td>
          </tr>

          <!-- 第五行（可选）：摘要关键词 -->
          <tr v-if="abstractSearchKeywords.length > 0">
            <td colspan="4">
              <div class="keyword-line">
                <span class="keyword-label">摘要关键词:</span>
                <div class="keyword-content">
                  <span v-for="(keyword, i) in abstractSearchKeywords" :key="i">
                    {{ keyword }}{{ i < abstractSearchKeywords.length - 1 ? ', ' : '' }}
                  </span>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 论文列表容器 -->
    <div class="paper-list-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div>
          <h3>正在加载 {{ selectedConference }} {{ selectedYear }} 数据...</h3>
          <div class="progress-container">
            <el-progress
              :percentage="Math.min(Math.round(loadingProgress / loadingTotal * 100), 100)"
              :format="() => `${loadingProgress}/${loadingTotal} 篇论文`"
              :stroke-width="20"
              status="success"
            />
          </div>
          <p>首批数据加载完成后将立即显示</p>
        </div>
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error-container">
        <el-empty
          description="加载数据失败"
          :image-size="200"
        >
          <template #description>
            <p>{{ error }}</p>
          </template>
          <el-button @click="loadPapers">重试</el-button>
        </el-empty>
      </div>

      <!-- 论文列表 -->
      <div v-else-if="paginatedPapers.length > 0">
        <paper-card
          v-for="(paper, index) in paginatedPapers"
          :key="paper.id || index"
          :paper="paper"
          :index="(currentPage - 1) * pageSize + index"
          :title-keywords="searchKeywords"
          :abstract-keywords="abstractSearchKeywords"
        />

        <!-- 底部分页导航 -->
        <div v-if="filteredPapers.length > pageSize" class="pagination-container">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            layout="prev, pager, next"
            :total="filteredPapers.length"
            :pager-count="7"
            @current-change="handleCurrentChange"
            background
            hide-on-single-page
          />
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="empty-container">
        <el-empty description="没有找到匹配的论文" />
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowDown, ArrowUp, Search } from '@element-plus/icons-vue'
import PaperCard from './PaperCard.vue'

export default {
  components: {
    ArrowDown,
    ArrowUp,
    'el-icon-search': Search,
    PaperCard
  },
  name: 'PaperList',
  data() {
    return {
      // 数据
      paperData: null,
      papers: [],
      filteredPapers: [],

      // 状态
      loading: false,
      tableLoading: false,
      error: null,

      // 加载进度
      loadingProgress: 0,
      loadingTotal: 100,
      showProgressBar: true,

      // 排序
      sortBy: 'order',
      sortDirection: 'asc',

      // 过滤和搜索
      selectedConference: 'CVPR',
      selectedYear: '', // 将在 created 钩子中设置为最新年份
      searchQuery: '',
      searchKeywords: [],
      abstractSearchQuery: '',
      abstractSearchKeywords: [],

      // 分页
      currentPage: 1,
      pageSize: 10,

      // 选项
      conferences: [],
      years: [],
      availableDatasets: [],

      // 配置数据
      conferencesConfig: {}
    }
  },

  computed: {
    paginatedPapers() {
      // 如果页面大小等于总数量，则显示全部
      if (this.pageSize >= this.filteredPapers.length) {
        return this.filteredPapers;
      }

      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredPapers.slice(start, end);
    },

    totalPages() {
      return Math.ceil(this.filteredPapers.length / this.pageSize);
    },

    // 根据所选会议返回可用的年份
    availableYears() {
      if (!this.selectedConference || !this.conferencesConfig[this.selectedConference]) {
        return [];
      }

      // 将年份转换为字符串并排序（降序）
      return this.conferencesConfig[this.selectedConference]
        .map(year => year.toString())
        .sort((a, b) => parseInt(b) - parseInt(a));
    }
  },

  async created() {
    console.log('组件创建，开始初始化...');

    try {
      // 首先扫描可用的数据集
      await this.scanAvailableDatasets();
      console.log('扫描完成，会议列表:', this.conferences);
      console.log('扫描完成，年份列表:', this.years);

      // 检查路由参数
      const { conference, year } = this.$route.query;
      console.log('路由参数:', { conference, year });

      // 设置默认值
      if (conference && this.conferences.includes(conference)) {
        this.selectedConference = conference;
        console.log('从路由参数设置会议:', this.selectedConference);
      } else {
        // 默认选择CVPR，如果可用的话
        this.selectedConference = this.conferences.includes('CVPR') ? 'CVPR' : this.conferences[0];
        console.log('设置默认会议:', this.selectedConference);
      }

      // 选择年份
      if (year && this.availableYears.includes(year)) {
        this.selectedYear = year;
        console.log('从路由参数设置年份:', this.selectedYear);
      } else if (this.availableYears.length > 0) {
        this.selectedYear = this.availableYears[0];
        console.log('设置默认年份:', this.selectedYear);
      }

      console.log(`尝试加载 ${this.selectedConference} ${this.selectedYear} 的数据`);

      // 尝试加载默认会议和年份的数据
      try {
        await this.loadPapers();
        console.log('成功加载默认数据');
      } catch (error) {
        console.error('无法加载默认会议和年份的数据，尝试加载其他可用数据集', error);

        // 尝试加载任何可用的数据集
        let loaded = false;
        for (const dataset of this.availableDatasets) {
          if (loaded) break;

          try {
            this.selectedConference = dataset.conference;
            this.selectedYear = dataset.year;
            await this.loadPapers();
            console.log(`成功加载 ${this.selectedConference} ${this.selectedYear} 的数据`);
            loaded = true;
          } catch (datasetError) {
            console.error(`无法加载 ${dataset.conference} ${dataset.year} 的数据`, datasetError);
            // 继续尝试下一个数据集
          }
        }

        // 如果所有数据集都加载失败，显示错误信息
        if (!loaded) {
          this.error = "无法加载任何数据集。请检查网络连接或联系管理员。";
        }
      }
    } catch (error) {
      console.error('初始化失败:', error);
      this.error = "初始化失败。请刷新页面重试。";
    }
  },

  methods: {
    // 从配置文件加载可用的会议和年份
    async scanAvailableDatasets() {
      try {
        console.log('开始从配置文件加载会议和年份信息...');

        const datasets = [];
        const conferencesSet = new Set();
        const yearsSet = new Set();

        // 从配置文件加载会议和年份信息
        const response = await fetch(`${import.meta.env.BASE_URL}data/conferences.json`);

        if (!response.ok) {
          throw new Error(`无法加载会议配置文件: ${response.status}`);
        }

        const config = await response.json();

        if (!config.conferences) {
          throw new Error('配置文件格式不正确，缺少conferences字段');
        }

        console.log('已加载会议配置:', config);

        // 保存完整的会议配置
        this.conferencesConfig = config.conferences;

        // 处理配置文件中的会议和年份
        for (const [conference, years] of Object.entries(config.conferences)) {
          conferencesSet.add(conference);

          for (const year of years) {
            const yearStr = year.toString();
            yearsSet.add(yearStr);

            datasets.push({
              conference: conference,
              year: yearStr,
              filename: `${conference}.${yearStr}.json`
            });
          }
        }

        console.log('配置加载完成，可用数据集数量:', datasets.length);

        // 更新会议和年份列表
        this.conferences = Array.from(conferencesSet).sort();
        this.years = Array.from(yearsSet).sort();
        this.availableDatasets = datasets;

        console.log('可用会议:', this.conferences);
        console.log('可用年份:', this.years);

        // 如果没有找到任何数据集
        if (datasets.length === 0) {
          throw new Error('配置文件中未定义任何数据集');
        }
      } catch (error) {
        console.error('加载会议配置失败:', error);
        this.error = '无法加载会议配置。请检查网络连接或联系管理员。';

        // 即使出错，也设置一些默认值
        this.conferences = ['CVPR', 'ICLR', 'NeurIPS'];
        this.years = ['2023', '2024'];
      }
    },

    loadPapers() {
      this.loading = true;
      this.error = null;
      this.currentPage = 1;
      this.papers = [];
      this.filteredPapers = [];
      this.loadingProgress = 0;
      this.loadingTotal = 100;

      // 创建一个缓存键
      const cacheKey = `papers_${this.selectedConference}_${this.selectedYear}`;

      // 检查缓存中是否有数据
      const cachedData = sessionStorage.getItem(cacheKey);
      if (cachedData) {
        try {
          console.log('从缓存加载数据...');
          const data = JSON.parse(cachedData);
          this.paperData = data;
          this.papers = data.papers || [];
          this.applySearch();
          this.loading = false;
          return Promise.resolve();
        } catch (e) {
          console.warn('缓存数据解析失败，将重新加载:', e);
          // 继续加载新数据
        }
      }

      return new Promise((resolve, reject) => {
        // 创建 Web Worker
        const worker = new Worker(new URL('../workers/paperLoader.js', import.meta.url), { type: 'module' });

        // 设置数据加载的 URL
        const url = `${import.meta.env.BASE_URL}data/${this.selectedConference}.${this.selectedYear}.json`;

        // 监听 Worker 消息
        worker.onmessage = (e) => {
          const { type, error } = e.data;

          switch (type) {
            case 'loading-start':
              console.log('开始加载数据...');
              break;

            case 'metadata':
              const { totalPapers, totalBatches } = e.data;
              console.log(`总论文数: ${totalPapers}, 总批次: ${totalBatches}`);
              this.loadingTotal = totalPapers;
              break;

            case 'batch':
              const { batch, batchIndex, startIndex, endIndex } = e.data;
              console.log(`接收批次 ${batchIndex + 1}, 论文 ${startIndex + 1} 到 ${endIndex}`);

              // 将批次数据添加到论文列表
              if (!this.papers) this.papers = [];
              this.papers.push(...batch);

              // 更新加载进度
              this.loadingProgress = endIndex;

              // 如果是第一批，立即应用搜索以显示一些结果
              if (batchIndex === 0) {
                this.applySearch();
              }
              break;

            case 'complete':
              console.log('数据加载完成');
              this.paperData = e.data.paperData;

              // 应用搜索过滤
              this.applySearch();

              // 缓存数据
              try {
                sessionStorage.setItem(cacheKey, JSON.stringify(this.paperData));
                console.log('数据已缓存');
              } catch (e) {
                console.warn('数据缓存失败:', e);
              }

              this.loading = false;
              worker.terminate();
              resolve();
              break;

            case 'error':
              console.error('数据加载失败:', error);
              this.error = `无法加载 ${this.selectedConference} ${this.selectedYear} 的数据: ${error}`;
              this.loading = false;
              worker.terminate();
              reject(new Error(error));
              break;
          }
        };

        // 处理 Worker 错误
        worker.onerror = (err) => {
          console.error('Worker 错误:', err);
          this.error = `加载数据时发生错误: ${err.message}`;
          this.loading = false;
          worker.terminate();
          reject(err);
        };

        // 启动 Worker
        worker.postMessage({
          url,
          batchSize: 200 // 每批加载 200 篇论文
        });
      });
    },

    handleSearch() {
      this.tableLoading = true;
      this.currentPage = 1;

      // 使用setTimeout来避免在输入时阻塞UI
      setTimeout(() => {
        this.applySearch();
        this.tableLoading = false;
      }, 300);
    },

    applySearch() {
      // 处理标题搜索关键词
      const titleKeywords = this.searchQuery
        ? this.searchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];
      this.searchKeywords = titleKeywords;

      // 处理摘要搜索关键词
      const abstractKeywords = this.abstractSearchQuery
        ? this.abstractSearchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];
      this.abstractSearchKeywords = abstractKeywords;

      // 如果两个搜索框都为空，显示所有论文
      if (titleKeywords.length === 0 && abstractKeywords.length === 0) {
        this.filteredPapers = [...this.papers];
        return;
      }



      this.filteredPapers = this.papers.filter(paper => {
        const title = (paper.title || '').toLowerCase();
        const abstract = (paper.abstract || '').toLowerCase();

        // 标题搜索逻辑
        let titleMatch = true;
        if (titleKeywords.length > 0) {
          titleMatch = titleKeywords.every(keyword => title.includes(keyword));
        }

        // 摘要搜索逻辑
        let abstractMatch = true;
        if (abstractKeywords.length > 0) {
          abstractMatch = abstractKeywords.every(keyword => abstract.includes(keyword));
        }

        // 如果标题搜索为空，只检查摘要匹配
        // 如果标题搜索不为空，则需要标题匹配，然后再检查摘要
        if (titleKeywords.length === 0) {
          return abstractMatch;
        } else {
          return titleMatch && (abstractKeywords.length === 0 || abstractMatch);
        }
      });

      // 应用排序
      this.sortPapers();


    },

    formatAuthorsDisplay(authors) {
      if (!authors) return '';

      // 如果是字符串，移除可能存在的引号
      if (typeof authors === 'string') {
        return authors.replace(/['"]/g, '');
      }

      // 如果是数组，将其连接成字符串，并移除引号
      if (Array.isArray(authors)) {
        return authors.join(', ').replace(/['"]/g, '');
      }

      return authors;
    },

    handleSizeChange(size) {
      this.pageSize = size;
      this.currentPage = 1; // 改变每页显示数量时，重置为第一页
    },

    handleCurrentChange(page) {
      this.currentPage = page;
    },





    // 高亮显示文本中的关键词
    highlightText(text, keywords) {
      if (!keywords || keywords.length === 0 || !text) {
        return text;
      }

      // 为了避免HTML注入，先对文本进行转义
      let highlightedText = this.escapeHtml(text);

      // 创建一个简单的正则表达式，匹配所有关键词（不区分大小写）
      for (const keyword of keywords) {
        if (keyword.trim() === '') continue;

        try {
          // 转义正则表达式中的特殊字符
          const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

          // 创建正则表达式，使用 'gi' 标志进行全局、不区分大小写的匹配
          const regex = new RegExp(`(${escapedKeyword})`, 'gi');

          // 替换匹配的文本
          highlightedText = highlightedText.replace(regex, '<span class="highlight">$1</span>');
        } catch (error) {
          console.error('Error highlighting keyword:', keyword, error);
        }
      }

      return highlightedText;
    },

    // 转义HTML特殊字符，防止XSS攻击
    escapeHtml(text) {
      return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    },

    // 排序相关方法
    handleSortChange() {
      this.sortPapers();
      this.currentPage = 1; // 重置为第一页
    },

    toggleSortDirection() {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      this.sortPapers();
      this.currentPage = 1; // 重置为第一页
    },

    sortPapers() {
      // 创建一个新数组进行排序，以保持响应式
      const sortedPapers = [...this.filteredPapers];

      sortedPapers.sort((a, b) => {
        let valueA, valueB;

        if (this.sortBy === 'order') {
          // 按索引排序（保持原始顺序）
          valueA = this.papers.indexOf(a);
          valueB = this.papers.indexOf(b);
        } else if (this.sortBy === 'title') {
          // 按标题排序
          valueA = (a.title || '').toLowerCase();
          valueB = (b.title || '').toLowerCase();
        }

        // 根据排序方向决定比较结果
        if (this.sortDirection === 'asc') {
          return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
        } else {
          return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
        }
      });

      this.filteredPapers = sortedPapers;
    },

    // 处理会议变更
    handleConferenceChange() {
      console.log('会议变更为:', this.selectedConference);

      // 如果有可用年份，选择最新的年份
      if (this.availableYears.length > 0) {
        this.selectedYear = this.availableYears[0];
        console.log('自动选择最新年份:', this.selectedYear);
      } else {
        this.selectedYear = '';
        console.log('没有可用年份');
      }

      // 加载论文数据
      this.loadPapers();
    }
  }
}
</script>

<style>
/* 容器样式 */
.filter-container {
  padding: 0;
  margin-bottom: 20px;
}

.paper-list-container {
  padding: 0;
  border-radius: 4px;
}

/* 表格样式 */
.filter-table {
  width: 100%;
  border-collapse: collapse;
  border: none;
}

.filter-table th {
  text-align: left;
  padding: 10px;
  width: 25%;
  font-size: var(--font-size-large);
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
  border: none;
}

.filter-table td {
  padding: 6px var(--spacing-medium);
  border: none;
}

.filter-table tr td:first-child {
  padding-left: 20px;
  padding-right: 10px;
}

/* 确保最后一列有正确的右边距 */
.filter-table tr td:last-child {
  padding-right: var(--spacing-medium);
}

.full-width-select {
  width: 100%;
}

/* 结果信息样式 */
.results-info {
  margin-top: 20px;
}

.conference-info {
  margin-bottom: 10px;
}

.conference-title {
  margin: 0;
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
}

.search-results-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
}

.sort-controls {
  display: flex;
  align-items: center;
}

.sort-buttons {
  display: flex;
  align-items: center;
  background-color: var(--bg-color-secondary);
  border-radius: var(--form-element-border-radius);
  padding: 2px;
}

.sort-direction-button {
  margin-left: 5px;
  height: var(--form-element-height);
  background-color: transparent !important;
  border: none !important;
  color: var(--text-color-primary) !important;
  font-size: var(--font-size-medium) !important;
  padding: 0 10px !important;
  transition: color 0.3s ease !important;
}

.sort-direction-button:hover {
  color: var(--highlight-color) !important;
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.search-result-text {
  font-size: var(--font-size-small);
  color: var(--text-color-regular);
  margin-bottom: 10px;
}

.total-count {
  margin-right: 10px;
  font-size: var(--font-size-small);
  color: var(--text-color-regular);
  white-space: nowrap;
}

.page-size-select {
  width: 120px;
  height: var(--form-element-height);
  margin-left: 10px;
}


/* 关键词样式 */
.keywords-container {
  margin-bottom: 15px;
}

.keywords-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-group {
  margin-right: 0;
}

.keyword-line {
  display: flex;
  align-items: center;
  font-size: var(--font-size-medium);
  flex-wrap: nowrap;
  white-space: nowrap;
}

.keyword-label {
  /* font-weight: var(--font-weight-bold); */
  /* color: var(--text-color-primary); */
  margin-right: 8px;
  flex-shrink: 0;
  display: inline-block;
  font-size: var(--font-size-medium);
  color: var(--text-color-regular);
}

.keyword-content {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  line-height: 28px;
  flex-wrap: wrap;
}

.keyword {
  color: var(--highlight-color);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-large);
  line-height: 28px;
  display: inline-block;
  vertical-align: bottom;
}

/* 加载状态样式 */
.loading-container {
  padding: 20px;
  text-align: center;
}

.progress-container {
  margin: 20px 0;
}

/* 错误提示样式 */
.error-container {
  padding: 40px;
  text-align: center;
}

/* 分页导航样式 */
.pagination-container {
  margin-top: 30px;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  width: 100%;
}

/* 无数据提示样式 */
.empty-container {
  padding: 40px;
  text-align: center;
}

/* 高亮样式 */
.highlight {
  background-color: rgba(210, 167, 106, 0.3);
  font-weight: bold;
}
</style>
