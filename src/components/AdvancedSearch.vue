<template>
  <div>
    <!-- 统一容器：包含过滤器、搜索和结果区域 -->
    <div class="filter-container">
      <!-- 过滤器和搜索区域 -->
      <el-row :gutter="5" class="filter-row top-controls-row">

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-select v-model="selectedConferences" placeholder="选择会议" @change="searchPapers" class="perfectly-aligned-control" multiple collapse-tags collapse-tags-tooltip>
              <el-option v-for="conference in conferences" :key="conference" :label="conference" :value="conference"></el-option>
            </el-select>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <el-row :gutter="5" class="year-range-row">
            <el-col :span="11" class="year-select-col">
              <div class="control-wrapper">
                <el-select v-model="startYear" placeholder="起始年份" @change="searchPapers" class="perfectly-aligned-control">
                  <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
                </el-select>
              </div>
            </el-col>
            <el-col :span="2" class="separator-container">
              <span class="separator-text">至</span>
            </el-col>
            <el-col :span="11" class="year-select-col">
              <div class="control-wrapper">
                <el-select v-model="endYear" placeholder="结束年份" @change="searchPapers" class="perfectly-aligned-control">
                  <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
                </el-select>
              </div>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-input v-model="searchQuery" placeholder="在标题中搜索" clearable @clear="searchQuery = ''; searchPapers()" @input="searchPapers" class="perfectly-aligned-control">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-input v-model="abstractSearchQuery" placeholder="在摘要中搜索" clearable @clear="abstractSearchQuery = ''; searchPapers()" @input="searchPapers" class="perfectly-aligned-control">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="5" class="filter-row"> 
        
        <el-col :span="6" class="search-results-info">
          <span>找到 {{ filteredPapers.length }} 篇匹配论文</span>
        </el-col>

        <el-col :span="6">
          <el-row :gutter="5" class="expand-row">
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.abstract}">
                <div class="button-text" @click="expandAllAbstracts">
                  <span class="no-padding-text">{{ expandAll.abstract ? '收起摘要' : '展开摘要' }}</span>
                </div>
              </div>
            </el-col>
            <!-- <el-col :span="1"></el-col>> -->
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.gemini}">
                <div class="button-text" @click="expandAllGemini">
                  <span class="no-padding-text">{{ expandAll.gemini ? '收起解读' : '展开解读' }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="6">
          <el-row :gutter="1" class="control-align-row">
            <el-col :span="20">
              <el-radio-group v-model="sortBy" @change="toggleSort" size="small" @dblclick="toggleSortDirection">
                <el-radio-button value="conference">默认</el-radio-button>
                <el-radio-button value="year">年份</el-radio-button>
                <el-radio-button value="title">标题</el-radio-button>
              </el-radio-group>
            </el-col>
            <el-col :span="4">
              <el-button @click="toggleSortDirection" :title="sortDirection === 'asc' ? '升序' : '降序'" size="small" class="sort-direction-btn">
                <span>{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </el-button>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="6">
          <el-row :gutter="5">
            <el-col :span="12">
              <span>共 {{ filteredPapers.length }} 篇</span>
            </el-col>
            <el-col :span="12">
              <el-select v-model="pageSize" @change="handleSizeChange" size="small">
                <el-option :value="10" label="10 篇/页" />
                <el-option :value="50" label="50 篇/页" />
                <el-option :value="100" label="100 篇/页" />
                <el-option :value="filteredPapers.length" label="全部显示" />
              </el-select>
            </el-col>
          </el-row>
        </el-col>

      </el-row>
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
          :expand-all="expandAll"
          @toggle-abstract="handleToggleAbstract"
        />

        <!-- 底部分页导航 -->
        <div v-if="filteredPapers.length > pageSize" class="pagination-container">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            layout="prev, pager, next, jumper"
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

    <!-- 回到顶部 -->
    <el-backtop :right="40" :bottom="40" />
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
      expandAll: {
        abstract: false,
        gemini: false
      },

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

  async mounted() {
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
          await this.searchPapers();
        }
      }
    } catch (error) {
      console.error('初始化失败:', error);
      this.error = "初始化失败。请刷新页面重试。";
    }
  },

  methods: {
    // 分页
    handleSizeChange(newPageSize) {
      this.pageSize = newPageSize;
      this.currentPage = 1; // 更改每页数量后，回到第一页
    },

    handleCurrentChange(newPage) {
      this.currentPage = newPage;
      window.scrollTo(0, 0); // 切换页面后滚动到顶部
    },
    
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
      if (!this.selectedConferences || this.selectedConferences.length === 0) {
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
        
        // 遍历所有选中的会议
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
      // 当排序字段改变时，重置排序方向为升序
      // v-model 已经更新了 this.sortBy
      this.sortDirection = 'asc';
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

    toggleAbstract(index) {
      // Vue 3 中直接修改对象属性即可触发响应式更新
      this.expandedAbstracts[index] = !this.expandedAbstracts[index];
    },

    handleToggleAbstract(index, isExpanded) {
      // 从子组件接收展开/收起事件
      this.expandedAbstracts[index] = isExpanded;
    },

    handleSizeChange(size) {
      this.currentPage = 1; // 改变每页显示数量时，重置为第一页
      this.pageSize = size;
    },

    expandAllAbstracts() {
      // 切换摘要的展开/收起状态
      this.expandAll.abstract = !this.expandAll.abstract;
      
      // 如果展开摘要，则确保解读是收起的
      if (this.expandAll.abstract) {
        this.expandAll.gemini = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },

    expandAllGemini() {
      // 切换解读的展开/收起状态
      this.expandAll.gemini = !this.expandAll.gemini;
      
      // 如果展开解读，则确保摘要是收起的
      if (this.expandAll.gemini) {
        this.expandAll.abstract = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },
  }
}
</script>

<style>

.filter-container{
  padding: 20px var(--content-padding, 0);
  margin-bottom: 20px;
  margin-top: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

/* Add paper-list-container style for consistent alignment */
.paper-list-container {
  padding: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

/* Add specific rules for perfect alignment */
.paper-list-container > div {
  padding: 0;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
}

/* Ensure no extra margins or padding in result items */
.result-item-container {
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}

/* 统一行高 */
.filter-container .el-button--default,
.filter-container .el-radio-button__inner,
.filter-container .el-input__wrapper {
  line-height: 1;
  height: 32px;
}

/* 确保顶部控件行完美对齐 */
.top-controls-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  height: 32px;
}

/* 每个控件容器垂直居中 */
.control-container {
  display: flex;
  align-items: center;
  height: 32px;
}

.expand-row{
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 控件包装容器，确保高度一致 */
.control-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 100%;
}

/* 年份选择列样式 */
.year-select-col {
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0;
}

/* 确保所有 Element Plus 表单控件的包装器都有一致的高度和对齐方式 */
.el-select .el-input__wrapper,
.el-input .el-input__wrapper {
  height: 32px !important;
  box-sizing: border-box !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  display: flex !important;
  align-items: center !important;
}

/* 确保下拉选择器的高度和行高一致 */
.el-select {
  width: 100%;
}

/* 精确设置表单组件的尺寸 */
.perfectly-aligned-control {
  width: 100%;
}

/* 确保输入框内部元素垂直居中 */
.el-input__inner {
  height: 30px !important;
  line-height: 30px !important;
  margin: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* 去除排序按钮的边框 */
.sort-direction-btn {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 16px;
}

/* 年份区间分隔符样式 */
.separator-text {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 展开按钮样式 */
.expand-row .el-button {
  width: 100%;
  height: 28px;
  padding: 0;
  margin: 0;
  font-size: 13px;
  transition: all 0.3s ease;
  border: none;
  background: transparent;
  box-shadow: none;
  color: #333;
}

.expand-button {
  position: relative;
}

/* 覆盖 Element Plus 的内部样式 */
.expand-button .el-button__content {
  margin-left: 0;
  padding-left: 0;
  justify-content: flex-start;
}

.text-left {
  text-align: left !important;
  padding-left: 0 !important;
}

/* 所有激活按钮特效已移除 */

/* 为了使按钮看起来更像第二张图中所示的效果 */
.expand-button {
  border: 1px dashed transparent !important;
  margin: 0;
}

/* 分隔符容器样式 */
.separator-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0;
}

/* 年份范围行样式 */
.year-range-row {
  display: flex;
  align-items: center;
  height: 32px;
  margin: 0;
}

/* 水平对齐筛选按钮 */
.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* 确保下拉框和按钮组的高度一致 */
.el-select,
.el-radio-group,
.el-input,
.el-button {
  height: 32px !important;
  line-height: 32px !important;
}

/* 精确设置输入框包装器的高度 */
.el-input__wrapper {
  height: 32px !important;
  line-height: 32px !important;
  padding: 0 11px !important;
}

/* 确保下拉框的高度一致 */
.el-select__wrapper {
  height: 32px !important;
  line-height: 32px !important;
}

/* 让按钮和图标垂直居中 */
.el-button {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保单选按钮组和按钮在同一水平线上 */
.el-radio-group {
  display: flex;
  align-items: center;
}

/* 确保无线电按钮内容垂直居中 */
.el-radio-button__inner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 标题对齐 */
.search-results-info {
  display: flex;
  align-items: center;
}

/* 让排序控件严格在同一水平线上对齐 */
.control-align-row {
  display: flex;
  align-items: center;
}

.control-align-row .el-radio-button,
.control-align-row .el-button {
  height: 32px;
  box-sizing: border-box;
}

/* 确保单选按钮和排序按钮的内容都处于中央位置 */
.control-align-row .el-radio-button__inner,
.control-align-row .el-button {
  padding: 0 12px;
  line-height: 30px;
  vertical-align: middle;
}

/* 强制文本完全贴左 */
.expand-row .el-button span {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0;
  margin: 0;
}

/* 覆盖按钮的默认边距 */
.expand-row .el-button--default {
  padding-left: 0 !important;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* 确保文字没有边距 */
.active-button > span {
  margin-left: 0;
}

/* 自定义按钮容器样式 */
.custom-button-wrapper {
  position: relative;
  display: block;
  padding: 0; /* 完全去除所有padding */
  cursor: pointer;
  border: none; /* 完全移除边框 */
  transition: all 0.3s;
  border-radius: 0; /* 移除圆角 */
  line-height: 1.5;
  height: 32px;
  box-sizing: border-box;
}

/* 激活状态的容器样式 - 不使用任何特效 */
/* 确保激活状态下的文本贴左 */
.active-wrapper .button-text {
  left: 0;
  padding-left: 0;
}

/* 按钮文字样式 */
.button-text {
  display: flex;
  align-items: center; /* 垂直居中 */
  text-align: left;
  padding: 0;
  margin: 0;
  padding-left: 0; /* 确保没有左padding */
  width: 100%;
  line-height: 30px; /* 与按钮高度一致，实现垂直居中 */
  white-space: nowrap; /* 防止文本换行 */
  position: absolute; /* 使用绝对定位确保完全靠左 */
  left: 0; /* 确保文本完全靠左边框 */
  top: 0; /* 顶部对齐 */
  height: 100%; /* 占满整个高度 */
  border-left: 0; /* 确保左边没有边框 */
}

/* 确保文字完全没有padding */
.no-padding-text {
  padding: 0;
  margin: 0;
  display: block;
  text-align: left;
}
</style>