<template>
  <div>
    <!-- 统一容器：包含过滤器、搜索和结果区域 -->
    <div class="filter-container">
      <!-- 过滤器和搜索区域 -->
      <table class="filter-table">
        <tr>
          <td style="width: 50%;">
            <div class="field-label">选择会议</div>
            <el-select v-model="selectedConferences" multiple placeholder="选择会议（可多选）" class="full-width-select" @change="searchPapers">
              <el-option v-for="conference in conferences" :key="conference" :label="conference" :value="conference"></el-option>
            </el-select>
          </td>
          <td style="width: 50%;">
            <div class="field-label">搜索标题</div>
            <el-input v-model="searchQuery" placeholder="在标题中搜索" clearable @clear="searchQuery = ''; searchPapers()" @input="searchPapers">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </td>
        </tr>
        <tr>
          <td style="width: 50%;">
            <div class="field-label">选择年份</div>
            <div class="year-range-container">
              <el-select v-model="startYear" placeholder="起始年份" class="year-select" @change="searchPapers" style="width: calc(50% - 14px);">
                <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
              </el-select>
              <span class="year-separator" style="width: 30px; text-align: center;">至</span>
              <el-select v-model="endYear" placeholder="结束年份" class="year-select" @change="searchPapers" style="width: calc(50% - 14px);">
                <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
              </el-select>
            </div>
          </td>
          <td style="width: 50%;">
            <div class="field-label">搜索摘要</div>
            <el-input v-model="abstractSearchQuery" placeholder="在摘要中搜索" clearable @clear="abstractSearchQuery = ''; searchPapers()" @input="searchPapers">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </td>
        </tr>

        <tr v-if="!loading && !error && searchPerformed">
          <td style="width: 40%; text-align: left;">
            <div v-if="filteredPapers.length > 0" class="search-results-info">
              <span>找到 {{ filteredPapers.length }} 篇匹配论文</span>
            </div>
          </td>
          <td style="width: 60%; text-align: right;">
            <div v-if="filteredPapers.length > 0" class="sort-controls">
              <div class="sort-buttons">
                <el-radio-group v-model="sortBy" @change="toggleSort" size="small">
                  <el-radio-button value="conference">会议</el-radio-button>
                  <el-radio-button value="year">年份</el-radio-button>
                  <el-radio-button value="title">标题</el-radio-button>
                </el-radio-group>
                <el-button @click="toggleSortDirection" :title="sortDirection === 'asc' ? '升序' : '降序'" class="sort-direction-button">
                  <span>{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </el-button>
              </div>
              <div class="pagination-controls">
                <span class="total-count">共 {{ filteredPapers.length }} 篇</span>
                <el-select v-model="pageSize" @change="handleSizeChange" size="small" class="page-size-select">
                  <el-option :value="10" label="10 篇/页" />
                  <el-option :value="50" label="50 篇/页" />
                  <el-option :value="100" label="100 篇/页" />
                  <el-option :value="filteredPapers.length" label="全部显示" />
                </el-select>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="searchKeywords.length > 0 || abstractSearchKeywords.length > 0">
          <td colspan="2">
            <div class="keywords-container">
              <div class="keywords-wrapper">
                <div v-if="searchKeywords.length > 0" class="keyword-group">
                  <div class="keyword-line">
                    <span class="keyword-label">标题关键词:</span>
                    <div class="keyword-content">
                      <span v-for="(keyword, i) in searchKeywords" :key="i">
                        <span class="keyword">{{ keyword }}</span>{{ i < searchKeywords.length - 1 ? ', ' : '' }}
                      </span>
                    </div>
                  </div>
                </div>
                <div v-if="abstractSearchKeywords.length > 0" class="keyword-group">
                  <div class="keyword-line">
                    <span class="keyword-label">摘要关键词:</span>
                    <div class="keyword-content">
                      <span v-for="(keyword, i) in abstractSearchKeywords" :key="i">
                        <span class="keyword">{{ keyword }}</span>{{ i < abstractSearchKeywords.length - 1 ? ', ' : '' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!-- 论文列表容器 -->
    <div class="paper-list-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div>
          <h3>正在加载数据...</h3>
          <div class="progress-container">
            <el-progress
              :percentage="loadingProgress"
              :stroke-width="20"
              status="success"
            />
          </div>
          <p>正在加载多个会议的数据，请稍候...</p>
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
          <el-button @click="searchPapers">重试</el-button>
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
          :expanded="expandedAbstracts[index]"
          @toggle-abstract="handleToggleAbstract"
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
        <el-empty :description="!searchPerformed ? '请选择搜索条件并点击搜索' : '未找到匹配的论文'" />
      </div>
    </div>
  </div>
</template>

<script>
import { Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue';
import PaperCard from './PaperCard.vue';

export default {
  components: {
    Search,
    ArrowUp,
    ArrowDown,
    PaperCard
  },
  name: 'AdvancedSearch',
  data() {
    return {
      // 数据
      allPapers: [],
      filteredPapers: [],
      loadedDatasets: new Set(),

      // 状态
      loading: false,
      error: null,
      expandedAbstracts: {},
      searchPerformed: false,

      // 加载进度
      loadingProgress: 0,
      loadedDatasetCount: 0,
      totalDatasetCount: 0,

      // 过滤和搜索
      selectedConferences: [],
      startYear: '',
      endYear: '',
      searchQuery: '',
      searchKeywords: [],
      abstractSearchQuery: '',
      abstractSearchKeywords: [],

      // 分页
      currentPage: 1,
      pageSize: 10,

      // 排序
      sortBy: 'conference',  // 'conference', 'year', 'title'
      sortDirection: 'asc',  // 'asc', 'desc'

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
    }
  },

  async created() {
    console.log('高级搜索组件创建，开始初始化...');
    try {
      // 加载会议和年份信息
      await this.scanAvailableDatasets();
      console.log('扫描完成，会议列表:', this.conferences);
      console.log('扫描完成，年份列表:', this.years);

      // 设置默认年份范围
      if (this.years.length > 0) {
        this.startYear = this.years[this.years.length - 1]; // 最早的年份
        this.endYear = this.years[0]; // 最新的年份
      }

      // 默认选择 CVPR 会议
      if (this.conferences.includes('CVPR')) {
        this.selectedConferences = ['CVPR'];

        // 获取 CVPR 最新年份
        const cvprYears = this.conferencesConfig['CVPR'] || [];
        if (cvprYears.length > 0) {
          // 按降序排序，取第一个（最新的）
          const latestYear = [...cvprYears].sort((a, b) => b - a)[0].toString();

          // 设置年份范围为最新年份
          this.startYear = latestYear;
          this.endYear = latestYear;

          console.log(`默认选择 CVPR ${latestYear} 数据`);

          // 自动执行搜索
          this.$nextTick(() => {
            this.searchPapers();
          });
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
        this.years = Array.from(yearsSet).sort((a, b) => parseInt(b) - parseInt(a)); // 降序排列
        this.availableDatasets = datasets;

        console.log('可用会议:', this.conferences);
        console.log('可用年份:', this.years);

        // 如果没有找到任何数据集
        if (datasets.length === 0) {
          throw new Error('配置文件中未定义任何数据集');
        }
      } catch (error) {
        console.error('加载会议和年份信息失败:', error);
        this.error = "无法加载会议和年份信息。请刷新页面重试。";
        throw error;
      }
    },

    // 搜索论文
    async searchPapers() {
      if (this.selectedConferences.length === 0) {
        this.error = "请至少选择一个会议";
        return;
      }

      if (!this.startYear || !this.endYear) {
        this.error = "请选择年份范围";
        return;
      }

      if (parseInt(this.startYear) > parseInt(this.endYear)) {
        this.error = "起始年份不能大于结束年份";
        return;
      }

      this.loading = true;
      this.error = null;
      this.searchPerformed = true;
      this.filteredPapers = [];
      this.currentPage = 1;

      try {
        // 获取所有需要加载的数据集
        const datasetsToLoad = [];
        for (const conference of this.selectedConferences) {
          const years = this.conferencesConfig[conference] || [];
          for (const year of years) {
            const yearStr = year.toString();
            if (parseInt(yearStr) >= parseInt(this.startYear) && parseInt(yearStr) <= parseInt(this.endYear)) {
              const datasetKey = `${conference}.${yearStr}`;
              // 只添加尚未加载的数据集
              if (!this.loadedDatasets.has(datasetKey)) {
                datasetsToLoad.push({
                  conference,
                  year: yearStr,
                  filename: `${conference}.${yearStr}.json`
                });
              }
            }
          }
        }

        console.log('需要加载的新数据集:', datasetsToLoad);

        // 加载新的数据集
        if (datasetsToLoad.length > 0) {
          await this.loadMultipleDatasets(datasetsToLoad);
        } else {
          console.log('所有需要的数据集已经加载过');
        }

        // 处理搜索关键词
        this.processSearchKeywords();

        // 应用搜索过滤
        this.applySearch();

        console.log('搜索完成，找到匹配论文数量:', this.filteredPapers.length);
      } catch (error) {
        console.error('搜索论文失败:', error);
        this.error = "搜索论文失败。请检查网络连接或重试。";
      } finally {
        this.loading = false;
      }
    },

    // 加载多个数据集
    async loadMultipleDatasets(datasets) {
      if (datasets.length === 0) {
        console.warn('没有符合条件的数据集需要加载');
        return; // 不抛出错误，而是返回空结果
      }

      // 重置加载进度
      this.loadingProgress = 0;
      this.loadedDatasetCount = 0;
      this.totalDatasetCount = datasets.length;

      // 使用缓存检查
      const cachedDatasets = [];
      const datasetsToLoad = [];

      // 检查哪些数据集可以从缓存加载
      for (const dataset of datasets) {
        const { conference, year } = dataset;
        const cacheKey = `papers_${conference}_${year}`;

        if (sessionStorage.getItem(cacheKey)) {
          cachedDatasets.push(dataset);
        } else {
          datasetsToLoad.push(dataset);
        }
      }

      // 先从缓存加载数据
      if (cachedDatasets.length > 0) {
        console.log(`从缓存加载 ${cachedDatasets.length} 个数据集`);
        for (const dataset of cachedDatasets) {
          await this.loadSingleDatasetFromCache(dataset);
          this.loadedDatasetCount++;
          this.loadingProgress = Math.round((this.loadedDatasetCount / this.totalDatasetCount) * 100);
        }
      }

      // 然后加载剩余的数据集
      if (datasetsToLoad.length > 0) {
        console.log(`从网络加载 ${datasetsToLoad.length} 个数据集`);

        // 一次加载一个数据集，以便更新进度
        for (const dataset of datasetsToLoad) {
          await this.loadSingleDataset(dataset);
          this.loadedDatasetCount++;
          this.loadingProgress = Math.round((this.loadedDatasetCount / this.totalDatasetCount) * 100);
        }
      }

      // 即使没有加载到论文，也不抛出错误，而是显示空结果
      if (this.allPapers.length === 0) {
        console.warn('未能加载任何论文数据');
      }
    },

    // 从缓存加载单个数据集
    async loadSingleDatasetFromCache(dataset) {
      const { conference, year } = dataset;
      const datasetKey = `${conference}.${year}`;
      const cacheKey = `papers_${conference}_${year}`;

      // 如果已经加载过这个数据集，跳过
      if (this.loadedDatasets.has(datasetKey)) {
        return;
      }

      try {
        const cachedData = sessionStorage.getItem(cacheKey);
        if (cachedData) {
          const data = JSON.parse(cachedData);

          if (data && Array.isArray(data.papers)) {
            // 将论文添加到总列表中
            this.allPapers = [...this.allPapers, ...data.papers];
            // 标记这个数据集已加载
            this.loadedDatasets.add(datasetKey);
            console.log(`从缓存成功加载 ${conference} ${year} 的数据，论文数量: ${data.papers.length}`);
          }
        }
      } catch (error) {
        console.error(`从缓存加载 ${conference} ${year} 的数据失败:`, error);
        // 如果从缓存加载失败，尝试从网络加载
        await this.loadSingleDataset(dataset);
      }
    },

    // 加载单个数据集
    async loadSingleDataset(dataset) {
      const { conference, year } = dataset;
      const datasetKey = `${conference}.${year}`;
      const cacheKey = `papers_${conference}_${year}`;

      // 如果已经加载过这个数据集，跳过
      if (this.loadedDatasets.has(datasetKey)) {
        return;
      }

      try {
        console.log(`开始加载 ${conference} ${year} 的数据...`);
        const response = await fetch(`${import.meta.env.BASE_URL}data/${conference}.${year}.json`);

        if (!response.ok) {
          console.warn(`无法加载 ${conference} ${year} 的数据: ${response.status}`);
          return;
        }

        const data = await response.json();

        if (data && Array.isArray(data.papers)) {
          // 将论文添加到总列表中
          this.allPapers = [...this.allPapers, ...data.papers];
          // 标记这个数据集已加载
          this.loadedDatasets.add(datasetKey);
          console.log(`成功加载 ${conference} ${year} 的数据，论文数量: ${data.papers.length}`);

          // 缓存数据
          try {
            sessionStorage.setItem(cacheKey, JSON.stringify(data));
            console.log(`已缓存 ${conference} ${year} 的数据`);
          } catch (e) {
            console.warn(`缓存 ${conference} ${year} 的数据失败:`, e);
          }
        } else {
          console.warn(`${conference} ${year} 的数据格式不符合预期`);
        }
      } catch (error) {
        console.error(`加载 ${conference} ${year} 的数据失败:`, error);
      }
    },

    // 处理搜索关键词
    processSearchKeywords() {
      // 处理标题搜索关键词
      this.searchKeywords = this.searchQuery
        ? this.searchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];

      // 处理摘要搜索关键词
      this.abstractSearchKeywords = this.abstractSearchQuery
        ? this.abstractSearchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];
    },

    // 应用搜索过滤
    applySearch() {
      // 如果两个搜索框都为空，显示所有符合会议和年份条件的论文
      if (this.searchKeywords.length === 0 && this.abstractSearchKeywords.length === 0) {
        // 过滤出符合当前选择的会议和年份范围的论文
        this.filteredPapers = this.allPapers.filter(paper => {
          const isConferenceMatch = this.selectedConferences.includes(paper.conference);
          const isYearMatch = parseInt(paper.year) >= parseInt(this.startYear) &&
                             parseInt(paper.year) <= parseInt(this.endYear);
          return isConferenceMatch && isYearMatch;
        });

        // 按会议和年份排序
        this.sortPapers();
        return;
      }



      this.filteredPapers = this.allPapers.filter(paper => {
        // 首先检查会议和年份是否匹配
        const isConferenceMatch = this.selectedConferences.includes(paper.conference);
        const isYearMatch = parseInt(paper.year) >= parseInt(this.startYear) &&
                           parseInt(paper.year) <= parseInt(this.endYear);

        if (!isConferenceMatch || !isYearMatch) {
          return false;
        }

        const title = (paper.title || '').toLowerCase();
        const abstract = (paper.abstract || '').toLowerCase();

        // 标题搜索逻辑
        let titleMatch = true;
        if (this.searchKeywords.length > 0) {
          titleMatch = this.searchKeywords.every(keyword => title.includes(keyword));
        }

        // 摘要搜索逻辑
        let abstractMatch = true;
        if (this.abstractSearchKeywords.length > 0) {
          abstractMatch = this.abstractSearchKeywords.every(keyword => abstract.includes(keyword));
        }

        // 如果标题搜索为空，只检查摘要匹配
        // 如果摘要搜索为空，只检查标题匹配
        // 如果两者都不为空，则需要同时满足标题和摘要的匹配条件
        if (this.searchKeywords.length === 0) {
          return abstractMatch;
        } else if (this.abstractSearchKeywords.length === 0) {
          return titleMatch;
        } else {
          return titleMatch && abstractMatch;
        }
      });

      // 按会议和年份排序
      this.sortPapers();


    },

    // 排序论文
    sortPapers() {
      this.filteredPapers.sort((a, b) => {
        let result = 0;

        // 根据选择的排序字段进行排序
        switch (this.sortBy) {
          case 'conference':
            result = a.conference.localeCompare(b.conference);
            break;
          case 'year':
            result = parseInt(a.year) - parseInt(b.year);
            break;
          case 'title':
            result = (a.title || '').localeCompare(b.title || '');
            break;
          default:
            result = parseInt(a.order) - parseInt(b.order);
        }

        // 应用排序方向
        if (this.sortDirection === 'desc') {
          result = -result;
        }

        // 如果主排序字段相同，则使用次要排序字段
        if (result === 0) {
          // 如果主排序不是会议，则按会议排序
          if (this.sortBy !== 'conference') {
            const conferenceCompare = a.conference.localeCompare(b.conference);
            if (conferenceCompare !== 0) return conferenceCompare;
          }

          // 如果主排序不是年份，则按年份排序（降序）
          if (this.sortBy !== 'year') {
            const yearCompare = parseInt(b.year) - parseInt(a.year);
            if (yearCompare !== 0) return yearCompare;
          }

          // 最后按序号排序
          return parseInt(a.order) - parseInt(b.order);
        }

        return result;
      });
    },

    // 切换排序方式
    toggleSort(field) {
      if (this.sortBy === field) {
        // 如果已经按此字段排序，则切换排序方向
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        // 否则，切换排序字段并设置为升序
        this.sortBy = field;
        this.sortDirection = 'asc';
      }

      // 重新排序
      this.sortPapers();
    },

    // 切换排序方向
    toggleSortDirection() {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      this.sortPapers();
    },

    // 重置筛选条件
    resetFilters() {
      // 清空搜索条件
      this.searchQuery = '';
      this.abstractSearchQuery = '';
      this.searchKeywords = [];
      this.abstractSearchKeywords = [];

      // 默认选择 CVPR 会议
      if (this.conferences.includes('CVPR')) {
        this.selectedConferences = ['CVPR'];

        // 获取 CVPR 最新年份
        const cvprYears = this.conferencesConfig['CVPR'] || [];
        if (cvprYears.length > 0) {
          // 按降序排序，取第一个（最新的）
          const latestYear = [...cvprYears].sort((a, b) => b - a)[0].toString();

          // 设置年份范围为最新年份
          this.startYear = latestYear;
          this.endYear = latestYear;


        } else {
          // 如果没有 CVPR 年份数据，使用全局年份范围
          if (this.years.length > 0) {
            this.startYear = this.years[this.years.length - 1]; // 最早的年份
            this.endYear = this.years[0]; // 最新的年份
          } else {
            this.startYear = '';
            this.endYear = '';
          }
        }
      } else {
        // 如果没有 CVPR 会议，清空会议选择
        this.selectedConferences = [];

        // 使用全局年份范围
        if (this.years.length > 0) {
          this.startYear = this.years[this.years.length - 1]; // 最早的年份
          this.endYear = this.years[0]; // 最新的年份
        } else {
          this.startYear = '';
          this.endYear = '';
        }
      }

      // 保留已加载的数据，但清空过滤结果
      this.filteredPapers = [];
      this.searchPerformed = false;
      this.error = null;

      // 重置排序为默认值
      this.sortBy = 'conference';
      this.sortDirection = 'asc';

      // 不清空 allPapers 和 loadedDatasets，以便保留已加载的数据
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

    toggleAbstract(index) {
      // Vue 3 中直接修改对象属性即可触发响应式更新
      this.expandedAbstracts[index] = !this.expandedAbstracts[index];
    },

    handleToggleAbstract(index, isExpanded) {
      // 从子组件接收展开/收起事件
      this.expandedAbstracts[index] = isExpanded;
    },

    handleSizeChange(size) {
      this.pageSize = size;
      this.currentPage = 1; // 改变每页显示数量时，重置为第一页
    },

    handleCurrentChange(page) {
      this.currentPage = page;
    },


  }
}
</script>

<style>
/* 页面标题样式 */
.page-title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
}

.page-title {
  margin: 0;
  font-size: var(--font-size-xxlarge);
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
}

/* 容器样式 */
.filter-container {
  padding: 20px;
  margin-bottom: 20px;
}

.paper-list-container {
  padding: 20px;
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
  font-size: var(--font-size-medium);
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
  border: none;
}

.filter-table td {
  padding: 10px;
  border: none;
  vertical-align: top;
}

.field-label {
  font-size: var(--font-size-small);
  color: var(--text-color-secondary);
  margin-bottom: 5px;
  font-weight: var(--font-weight-medium);
}

.full-width-select {
  width: 100%;
}

.year-range-container {
  display: flex;
  align-items: center;
}

.year-select {
  width: 45%;
}

.year-separator {
  margin: 0 10px;
}

.search-button-container {
  padding: 10px;
  text-align: center;
}

.search-button {
  margin-right: 10px;
}

/* 结果信息样式 */
.results-info {
  margin-top: 20px;
}

.search-results-info {
  display: flex;
  align-items: center;
  height: 32px;
  font-size: var(--font-size-small);
  color: var(--text-color-secondary);
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
  justify-content: space-between;
  width: 100%;
}

.sort-buttons {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
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
  flex: 1 1 auto;
  text-align: right;
}

.total-count {
  margin-right: 10px;
  white-space: nowrap;
  font-size: var(--font-size-small);
  color: var(--text-color-secondary);
}

.page-size-select {
  width: 120px;
  height: var(--form-element-height);
  flex: 0 0 auto;
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
  font-size: var(--font-size-small);
  flex-wrap: nowrap;
  white-space: nowrap;
  margin-bottom: 4px;
}

.keyword-label {
  font-weight: var(--font-weight-medium);
  color: var(--text-color-secondary);
  margin-right: 8px;
  flex-shrink: 0;
  display: inline-block;
  font-size: var(--font-size-small);
}

.keyword-content {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  line-height: 22px;
  flex-wrap: wrap;
}

.keyword {
  color: inherit;
  font-weight: normal;
  font-size: var(--font-size-small);
  line-height: 22px;
  display: inline-block;
  vertical-align: bottom;
  background-color: rgba(233, 185, 110, 0.3);
  padding: 0 4px;
  border-radius: 4px;
  margin: 0 2px;
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
  background-color: rgba(233, 185, 110, 0.3);
  font-weight: normal;
  color: inherit;
  padding: 0 3px;
  border-radius: 4px;
  display: inline-block;
  position: relative;
  line-height: 1.2;
}
</style>

