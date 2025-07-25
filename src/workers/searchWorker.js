// 搜索Worker - 在后台线程中执行搜索操作
let searchCache = new Map();
let searchIndex = null;
let performanceStats = {
  totalSearches: 0,
  averageSearchTime: 0,
  indexCreationTime: 0,
  cacheHits: 0,
  lastIndexSize: 0
};

// 性能监控辅助函数
function logPerformance(operation, duration, details = {}) {
  console.log(`[Worker Performance] ${operation}: ${duration.toFixed(2)}ms`, details);
}

// 创建高效的搜索索引 - 渐进式版本
function createSearchIndex(papers) {
  console.log('开始创建搜索索引，论文数量:', papers.length);
  const startTime = performance.now();
  
  const index = {
    papers: [],
    titleIndex: new Map(),
    abstractIndex: new Map(),
    conferenceIndex: new Map(),
    yearIndex: new Map()
  };

  // 分批处理，避免长时间阻塞
  const batchSize = 1000;
  let processed = 0;

  for (let i = 0; i < papers.length; i += batchSize) {
    const batch = papers.slice(i, i + batchSize);
    
    batch.forEach((paper, batchIdx) => {
      const idx = i + batchIdx;
      
      // 预处理论文数据
      const processedPaper = {
        ...paper,
        titleLower: (paper.title || '').toLowerCase(),
        abstractLower: (paper.abstract || '').toLowerCase(),
        conferenceLower: (paper.conference || '').toLowerCase(),
        yearNum: parseInt(paper.year) || 0
      };
      
      index.papers.push(processedPaper);

      // 构建倒排索引
      buildInvertedIndex(processedPaper.titleLower, idx, index.titleIndex);
      buildInvertedIndex(processedPaper.abstractLower, idx, index.abstractIndex);
      
      // 会议索引
      if (!index.conferenceIndex.has(paper.conference)) {
        index.conferenceIndex.set(paper.conference, new Set());
      }
      index.conferenceIndex.get(paper.conference).add(idx);
      
      // 年份索引
      const year = processedPaper.yearNum;
      if (!index.yearIndex.has(year)) {
        index.yearIndex.set(year, new Set());
      }
      index.yearIndex.get(year).add(idx);
    });

    processed += batch.length;
    
    // 每处理一批后，让出控制权避免阻塞
    if (i + batchSize < papers.length) {
      // 使用setTimeout(0)让出控制权，但在Worker中这不会真正异步
      // 只能通过消息机制来报告进度
      if (processed % 5000 === 0) {
        console.log(`索引构建进度: ${processed}/${papers.length}`);
      }
    }
  }

  const endTime = performance.now();
  console.log(`搜索索引创建完成，耗时 ${(endTime - startTime).toFixed(2)}ms`);
  
  return index;
}

// 构建倒排索引 - 优化版本
function buildInvertedIndex(text, docId, index) {
  if (!text) return;
  
  // 更智能的分词策略
  const words = text
    .toLowerCase()
    .replace(/[^\w\s-]/g, ' ') // 保留连字符，去除其他标点
    .split(/\s+/)
    .filter(word => word.length > 1) // 过滤掉单字符词
    .filter(word => !isStopWord(word)); // 过滤停用词
  
  // 为每个词及其子串建立索引
  words.forEach(word => {
    // 完整词索引
    if (!index.has(word)) {
      index.set(word, new Set());
    }
    index.get(word).add(docId);
    
    // 为长词建立前缀索引，便于快速匹配
    if (word.length > 3) {
      for (let i = 3; i <= Math.min(word.length, 6); i++) {
        const prefix = word.substring(0, i);
        if (!index.has(prefix)) {
          index.set(prefix, new Set());
        }
        index.get(prefix).add(docId);
      }
    }
  });
}

// 简单的停用词过滤
function isStopWord(word) {
  const stopWords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
  ]);
  return stopWords.has(word);
}

// 高效搜索函数
function searchPapers(searchParams) {
  const overallStartTime = performance.now();
  
  const {
    selectedConferences,
    startYear,
    endYear,
    titleKeywords,
    abstractKeywords
  } = searchParams;

  if (!searchIndex) {
    console.error('搜索索引未初始化');
    return [];
  }

  // 创建缓存键
  const cacheKey = JSON.stringify(searchParams);
  
  // 检查缓存
  if (searchCache.has(cacheKey)) {
    console.log('使用缓存结果');
    performanceStats.cacheHits++;
    return searchCache.get(cacheKey);
  }

  console.log('执行新搜索，参数:', searchParams);
  const startTime = performance.now();
  
  // 统计信息
  const searchStats = {
    totalPapers: searchIndex.papers.length,
    conferenceFiltered: 0,
    yearFiltered: 0,
    keywordFiltered: 0,
    finalResults: 0,
    steps: []
  };

  // 第一步：使用索引快速过滤会议和年份
  let candidateIndices = new Set();
  let isFirstFilter = true;
  const conferenceFilterStart = performance.now();

  // 会议过滤 - 交集操作
  selectedConferences.forEach(conference => {
    const conferenceIndices = searchIndex.conferenceIndex.get(conference);
    if (conferenceIndices) {
      if (isFirstFilter) {
        candidateIndices = new Set(conferenceIndices);
        isFirstFilter = false;
      } else {
        // 取交集
        const intersection = new Set();
        for (const idx of candidateIndices) {
          if (conferenceIndices.has(idx)) {
            intersection.add(idx);
          }
        }
        candidateIndices = intersection;
      }
    }
  });

  if (candidateIndices.size === 0) {
    console.log('会议过滤后无结果');
    return [];
  }

  // 年份过滤 - 早期终止优化
  const startYearNum = parseInt(startYear);
  const endYearNum = parseInt(endYear);
  const yearFilteredIndices = new Set();

  for (const idx of candidateIndices) {
    const paper = searchIndex.papers[idx];
    if (paper.yearNum >= startYearNum && paper.yearNum <= endYearNum) {
      yearFilteredIndices.add(idx);
    }
  }

  candidateIndices = yearFilteredIndices;

  if (candidateIndices.size === 0) {
    console.log('年份过滤后无结果');
    return [];
  }

  // 第二步：关键词搜索优化
  if (titleKeywords.length > 0 || abstractKeywords.length > 0) {
    let keywordFilteredIndices = candidateIndices;

    // 标题关键词过滤 - 优化版本
    if (titleKeywords.length > 0) {
      for (const keyword of titleKeywords) {
        const matchingIndices = new Set();
        let foundInIndex = false;
        
        // 优先使用倒排索引快速查找
        for (const [word, docIndices] of searchIndex.titleIndex) {
          if (word.includes(keyword)) {
            foundInIndex = true;
            for (const idx of docIndices) {
              if (keywordFilteredIndices.has(idx)) {
                matchingIndices.add(idx);
              }
            }
          }
        }
        
        // 如果索引查找无结果，使用直接搜索（备用方案）
        if (!foundInIndex || matchingIndices.size === 0) {
          for (const idx of keywordFilteredIndices) {
            if (searchIndex.papers[idx].titleLower.includes(keyword)) {
              matchingIndices.add(idx);
            }
          }
        }
        
        keywordFilteredIndices = matchingIndices;
        
        // 早期终止：如果某个关键词匹配为空，整个结果为空
        if (keywordFilteredIndices.size === 0) {
          console.log(`标题关键词 "${keyword}" 无匹配结果`);
          return [];
        }
      }
    }

    // 摘要关键词过滤 - 优化版本
    if (abstractKeywords.length > 0) {
      for (const keyword of abstractKeywords) {
        const matchingIndices = new Set();
        let foundInIndex = false;
        
        // 优先使用倒排索引快速查找
        for (const [word, docIndices] of searchIndex.abstractIndex) {
          if (word.includes(keyword)) {
            foundInIndex = true;
            for (const idx of docIndices) {
              if (keywordFilteredIndices.has(idx)) {
                matchingIndices.add(idx);
              }
            }
          }
        }
        
        // 如果索引查找无结果，使用直接搜索（备用方案）
        if (!foundInIndex || matchingIndices.size === 0) {
          for (const idx of keywordFilteredIndices) {
            if (searchIndex.papers[idx].abstractLower.includes(keyword)) {
              matchingIndices.add(idx);
            }
          }
        }
        
        keywordFilteredIndices = matchingIndices;
        
        // 早期终止：如果某个关键词匹配为空，整个结果为空
        if (keywordFilteredIndices.size === 0) {
          console.log(`摘要关键词 "${keyword}" 无匹配结果`);
          return [];
        }
      }
    }

    candidateIndices = keywordFilteredIndices;
  }

  // 获取最终结果
  const results = Array.from(candidateIndices).map(idx => searchIndex.papers[idx]);

  const endTime = performance.now();
  const searchTime = endTime - startTime;
  performanceStats.totalSearches++;
  performanceStats.averageSearchTime = ((performanceStats.averageSearchTime * (performanceStats.totalSearches - 1)) + searchTime) / performanceStats.totalSearches;
  console.log(`搜索完成，耗时 ${(endTime - startTime).toFixed(2)}ms，找到论文数量: ${results.length}`);

  // 缓存结果（LRU策略）
  if (searchCache.size > 100) {
    // 清理缓存，保留最近的50个结果
    const entries = Array.from(searchCache.entries());
    searchCache.clear();
    entries.slice(-50).forEach(([key, value]) => {
      searchCache.set(key, value);
    });
  }
  
  searchCache.set(cacheKey, results);
  
  return results;
}

// 排序函数
function sortPapers(papers, sortBy, sortDirection) {
  return papers.sort((a, b) => {
    let result = 0;

    switch (sortBy) {
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
        result = parseInt(a.order || 0) - parseInt(b.order || 0);
    }

    if (sortDirection === 'desc') {
      result = -result;
    }

    // 次要排序
    if (result === 0) {
      if (sortBy !== 'conference') {
        const conferenceCompare = a.conference.localeCompare(b.conference);
        if (conferenceCompare !== 0) return conferenceCompare;
      }

      if (sortBy !== 'year') {
        const yearCompare = parseInt(b.year) - parseInt(a.year);
        if (yearCompare !== 0) return yearCompare;
      }

      return parseInt(a.order || 0) - parseInt(b.order || 0);
    }

    return result;
  });
}

// 监听主线程消息
self.onmessage = function(e) {
  try {
    const { type, data } = e.data;

    switch (type) {
      case 'updatePapers':
        try {
          // 创建搜索索引
          console.log('Worker接收到论文数据，开始创建索引...');
          if (!data || !Array.isArray(data.papers)) {
            throw new Error('论文数据格式错误');
          }
          
          searchIndex = createSearchIndex(data.papers);
          self.postMessage({
            type: 'papersUpdated',
            success: true,
            count: data.papers.length
          });
        } catch (error) {
          console.error('创建搜索索引失败:', error);
          self.postMessage({
            type: 'papersUpdated',
            success: false,
            error: error.message
          });
        }
        break;

      case 'search':
        try {
          if (!searchIndex) {
            self.postMessage({
              type: 'searchResult',
              success: false,
              error: '论文数据未加载'
            });
            return;
          }

          const searchParams = data.searchParams;
          if (!searchParams) {
            throw new Error('搜索参数缺失');
          }
          
          const searchStartTime = performance.now();
          
          // 执行搜索
          const searchResults = searchPapers(searchParams);
          
          const searchEndTime = performance.now();
          const searchTime = searchEndTime - searchStartTime;
          
          // 执行排序
          const sortedResults = sortPapers(
            searchResults, 
            data.sortBy || 'conference', 
            data.sortDirection || 'asc'
          );

          self.postMessage({
            type: 'searchResult',
            success: true,
            results: sortedResults,
            count: sortedResults.length,
            searchTime: searchTime,
            searchParams
          });
        } catch (error) {
          console.error('搜索执行失败:', error);
          self.postMessage({
            type: 'searchResult',
            success: false,
            error: error.message
          });
        }
        break;

      case 'clearCache':
        try {
          searchCache.clear();
          self.postMessage({
            type: 'cacheCleared',
            success: true
          });
        } catch (error) {
          self.postMessage({
            type: 'cacheCleared',
            success: false,
            error: error.message
          });
        }
        break;

      default:
        self.postMessage({
          type: 'error',
          success: false,
          error: `未知的消息类型: ${type}`
        });
    }
  } catch (error) {
    console.error('Worker消息处理错误:', error);
    self.postMessage({
      type: 'error',
      success: false,
      error: `消息处理错误: ${error.message}`
    });
  }
};
